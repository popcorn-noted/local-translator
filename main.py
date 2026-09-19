import sys
import asyncio
from tetherto.qvac_sdk import Client, load_model, translate

async def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Enter Spanish text to translate (empty line to exit):")
        text = sys.stdin.readline().strip()

    if not text:
        return

    try:
        async with Client() as client:
            transport = client.transport
            model_id = await load_model(transport, model_src="translate")
            run = translate(transport, model_id=model_id, text=text, model_type="translate", to="en", stream=False)
            translation = await run.text
            print(translation)
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure QVAC worker is installed: npm install -g @qvac/sdk && python -m tetherto.qvac_sdk install-worker")

if __name__ == "__main__":
    asyncio.run(main())
