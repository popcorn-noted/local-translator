"""Local Translator - a modern desktop GUI for the QVAC SDK.
 
Setup:   pip install customtkinter
Run:     python gui.py
 
The model loads once when the window opens and stays loaded, so every
translation after the first one is quick.
"""
import asyncio
import queue
import threading
import tkinter.messagebox as messagebox
import traceback
 
import customtkinter as ctk
 
from tetherto.qvac_sdk import Client, load_model, translate, unload_model
from tetherto.qvac_sdk.models import SALAMANDRATA_2B_INST_Q4
 
MODEL = SALAMANDRATA_2B_INST_Q4
 
# Display name -> language code sent to the model.
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Catalan": "ca",
    "Dutch": "nl",
}
 
# ---- Theme (each colour is a (light, dark) pair) --------------------------
ACCENT = "#7C5CFF"
ACCENT_HOVER = "#6A49F0"
BG = ("#F1F2F9", "#0D0E16")
CARD = ("#FFFFFF", "#171826")
BORDER = ("#DDDFEC", "#272944")
TEXT = ("#191B2C", "#ECEEFA")
MUTED = ("#6A6E8A", "#8A8EAE")
GREEN = ("#12A66A", "#3DDC97")
RED = ("#D64545", "#FF6B6B")
SOFT_BTN = ("#E8E9F5", "#22243B")
SOFT_BTN_HOVER = ("#DADCEE", "#2C2F4D")
 
FONT = "Segoe UI"  # falls back automatically on macOS / Linux
 
ctk.set_appearance_mode("dark")
 
 
class Backend(threading.Thread):
    """Runs the SDK's asyncio code in its own thread so the window never freezes.
 
    Talks to the GUI only through `events` (a thread-safe queue).
    """
 
    def __init__(self, events: "queue.Queue"):
        super().__init__(daemon=True)
        self.events = events
        self.loop = None
        self.jobs = None
 
    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.jobs = asyncio.Queue()
        self.loop = loop
        loop.run_until_complete(self._main())
 
    # ---- called from the GUI thread -------------------------------------
    def submit(self, text: str, lang: str) -> None:
        self.loop.call_soon_threadsafe(self.jobs.put_nowait, (text, lang))
 
    def stop(self) -> None:
        if self.loop is not None:
            self.loop.call_soon_threadsafe(self.jobs.put_nowait, None)
 
    # ---- runs in the backend thread -------------------------------------
    def _on_progress(self, p) -> None:
        self.events.put(("progress", (p.percentage, p.downloaded, p.total)))
 
    async def _main(self) -> None:
        try:
            async with Client() as client:
                transport = client.transport
                model_id = await load_model(
                    transport, model_src=MODEL, on_progress=self._on_progress
                )
                self.events.put(("ready", None))
                try:
                    while True:
                        job = await self.jobs.get()
                        if job is None:
                            break
                        await self._translate(transport, model_id, *job)
                finally:
                    await unload_model(transport, model_id=model_id)
        except Exception:
            self.events.put(("fatal", traceback.format_exc()))
 
    async def _translate(self, transport, model_id: str, text: str, lang: str) -> None:
        try:
            run = translate(
                transport,
                model_id=model_id,
                text=text,
                model_type="llamacpp-completion",
                to=lang,
                stream=True,
            )
            async for token in run.token_stream:
                self.events.put(("token", token))
            self.events.put(("done", None))
        except Exception:
            self.events.put(("error", traceback.format_exc()))
 
 
class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Local Translator")
        self.geometry("1040x680")
        self.minsize(820, 560)
        self.configure(fg_color=BG)
 
        self.events: "queue.Queue" = queue.Queue()
        self.backend = Backend(self.events)
        self.ready = False
 
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
 
        self.backend.start()
        self.after(50, self._poll)
 
    # ---- layout ----------------------------------------------------------
    def _build_ui(self) -> None:
        f_title = ctk.CTkFont(family=FONT, size=32, weight="bold")
        f_sub = ctk.CTkFont(family=FONT, size=15)
        f_label = ctk.CTkFont(family=FONT, size=16, weight="bold")
        f_small = ctk.CTkFont(family=FONT, size=13)
        f_btn = ctk.CTkFont(family=FONT, size=17, weight="bold")
        f_body = ctk.CTkFont(family=FONT, size=20)
 
        self.columnconfigure((0, 1), weight=1, uniform="cards")
        self.rowconfigure(1, weight=1)
 
        # ---------- header ----------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=28, pady=(24, 14))
        header.columnconfigure(0, weight=1)
 
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_box, text="Local Translator", font=f_title,
                     text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Private and offline. Everything runs on your computer.",
                     font=f_sub, text_color=MUTED).pack(anchor="w")
 
        self.theme_switch = ctk.CTkSwitch(
            header, text="Dark mode", font=f_small, text_color=MUTED,
            progress_color=ACCENT, command=self._toggle_theme,
        )
        self.theme_switch.select()
        self.theme_switch.grid(row=0, column=1, sticky="e")
 
        # ---------- input card ----------
        left = self._card(0)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
 
        lh = ctk.CTkFrame(left, fg_color="transparent")
        lh.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 6))
        lh.columnconfigure(0, weight=1)
        ctk.CTkLabel(lh, text="YOUR TEXT", font=f_label, text_color=MUTED).grid(
            row=0, column=0, sticky="w")
        ctk.CTkButton(lh, text="Clear", width=72, height=32, font=f_small,
                      fg_color=SOFT_BTN, hover_color=SOFT_BTN_HOVER, text_color=TEXT,
                      corner_radius=8, command=self._clear).grid(row=0, column=1)
 
        self.input = ctk.CTkTextbox(left, wrap="word", font=f_body, text_color=TEXT,
                                    fg_color=CARD, border_width=0, undo=True)
        self.input.grid(row=1, column=0, sticky="nsew", padx=14, pady=0)
        self.input.bind("<Control-Return>", self._on_ctrl_enter)
        self.input.bind("<KeyRelease>", self._update_count)
 
        lf = ctk.CTkFrame(left, fg_color="transparent")
        lf.grid(row=2, column=0, sticky="ew", padx=20, pady=(8, 18))
        lf.columnconfigure(0, weight=1)
        self.count = ctk.CTkLabel(lf, text="0 characters", font=f_small, text_color=MUTED)
        self.count.grid(row=0, column=0, sticky="w")
        self.btn = ctk.CTkButton(
            lf, text="Translate   \u21B5", width=170, height=46, font=f_btn,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#FFFFFF",
            text_color_disabled=("#9A9DB8", "#5C5F7E"), corner_radius=12,
            state="disabled", command=self.translate_clicked,
        )
        self.btn.grid(row=0, column=1)
 
        # ---------- output card ----------
        right = self._card(1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
 
        rh = ctk.CTkFrame(right, fg_color="transparent")
        rh.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 6))
        rh.columnconfigure(1, weight=1)
        ctk.CTkLabel(rh, text="TRANSLATE TO", font=f_label, text_color=MUTED).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.lang = ctk.CTkOptionMenu(
            rh, values=list(LANGUAGES), width=150, height=34, font=f_small,
            dropdown_font=f_small, fg_color=SOFT_BTN, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER, text_color=TEXT,
            dropdown_fg_color=CARD, dropdown_text_color=TEXT,
            dropdown_hover_color=SOFT_BTN_HOVER, corner_radius=8,
        )
        self.lang.set("English")
        self.lang.grid(row=0, column=1, sticky="w")
        self.copy_btn = ctk.CTkButton(
            rh, text="Copy", width=72, height=32, font=f_small,
            fg_color=SOFT_BTN, hover_color=SOFT_BTN_HOVER, text_color=TEXT,
            corner_radius=8, command=self._copy,
        )
        self.copy_btn.grid(row=0, column=2)
 
        self.output = ctk.CTkTextbox(right, wrap="word", font=f_body, text_color=TEXT,
                                     fg_color=CARD, border_width=0, state="disabled")
        self.output.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 18))
 
        # ---------- status bar ----------
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, columnspan=2, sticky="ew", padx=28, pady=(14, 20))
        bottom.columnconfigure(0, weight=1)
        self.status = ctk.CTkLabel(bottom, text="Starting up...", font=f_small,
                                   text_color=MUTED, anchor="w")
        self.status.grid(row=0, column=0, sticky="w")
        self.progress = ctk.CTkProgressBar(bottom, height=6, progress_color=ACCENT,
                                           fg_color=BORDER)
        self.progress.set(0)
        self.progress.grid(row=1, column=0, sticky="ew", pady=(6, 0))
 
    def _card(self, column: int) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self, fg_color=CARD, border_width=1, border_color=BORDER,
                            corner_radius=18)
        card.grid(row=1, column=column, sticky="nsew",
                  padx=(28, 10) if column == 0 else (10, 28))
        return card
 
    # ---- actions ---------------------------------------------------------
    def _toggle_theme(self) -> None:
        ctk.set_appearance_mode("dark" if self.theme_switch.get() else "light")
 
    def _update_count(self, _event=None) -> None:
        n = len(self.input.get("1.0", "end").strip())
        self.count.configure(text=f"{n:,} character{'s' if n != 1 else ''}")
 
    def _on_ctrl_enter(self, _event) -> str:
        self.translate_clicked()
        return "break"  # stop Tk from inserting a newline
 
    def translate_clicked(self) -> None:
        if not self.ready or str(self.btn.cget("state")) == "disabled":
            return
        text = self.input.get("1.0", "end").strip()
        if not text:
            return
        self._set_output("")
        self.btn.configure(state="disabled", text="Translating...")
        self._set_status("Translating...", MUTED)
        self.backend.submit(text, LANGUAGES[self.lang.get()])
 
    def _clear(self) -> None:
        self.input.delete("1.0", "end")
        self._set_output("")
        self._update_count()
        self.input.focus_set()
 
    def _copy(self) -> None:
        result = self.output.get("1.0", "end").strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            self._set_status("Copied to clipboard.", GREEN)
 
    def _set_status(self, text: str, color=MUTED) -> None:
        self.status.configure(text=text, text_color=color)
 
    def _set_output(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")
 
    def _append_output(self, token: str) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", token)
        self.output.see("end")
        self.output.configure(state="disabled")
 
    def _enable_translate(self) -> None:
        self.btn.configure(state="normal", text="Translate   \u21B5")
 
    # ---- backend events --------------------------------------------------
    def _poll(self) -> None:
        try:
            while True:
                kind, data = self.events.get_nowait()
                self._handle(kind, data)
        except queue.Empty:
            pass
        self.after(50, self._poll)
 
    def _handle(self, kind: str, data) -> None:
        if kind == "progress":
            pct, done, total = data
            self.progress.set(min(max(pct / 100, 0), 1))
            self._set_status(
                f"Loading model...  {pct:.0f}%   ({done / 1_048_576:,.0f} / "
                f"{total / 1_048_576:,.0f} MB)", MUTED)
        elif kind == "ready":
            self.ready = True
            self.progress.set(1)
            self._enable_translate()
            self._set_status("Ready", GREEN)
            self.input.focus_set()
        elif kind == "token":
            self._append_output(data)
        elif kind == "done":
            self._enable_translate()
            self._set_status("Done", GREEN)
        elif kind == "error":
            self._enable_translate()
            self._set_status("Translation failed", RED)
            messagebox.showerror("Translation error", data)
        elif kind == "fatal":
            self._set_status("Backend stopped", RED)
            messagebox.showerror("Backend error", data)
 
    def _on_close(self) -> None:
        self.backend.stop()
        self.backend.join(timeout=5)  # give the model a moment to unload
        self.destroy()
 
 
if __name__ == "__main__":
    App().mainloop()
 