# Local Translator (Spanish → English)

A simple CLI app that uses QVAC to translate Spanish text to English entirely on-device.

## Requirements

- Python 3.8+
- `tetherto-qvac-sdk>=0.19.0`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Via command-line argument
python main.py "Hola, ¿cómo estás?"

# Via stdin
echo "Hola, ¿cómo estás?" | python main.py
```

## How It Works

1. The app loads the QVAC translation model.
2. It accepts Spanish text via CLI argument or stdin.
3. It calls `sdk.translate()` to translate to English.
4. The translation is printed to stdout.

No API keys, no cloud usage — everything runs locally.
