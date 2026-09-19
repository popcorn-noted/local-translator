# Local Translator (Spanish → English)

A simple CLI app that uses QVAC to translate text entirely on-device.

## Requirements

- Python 3.8+
- Node.js 18+ (for QVAC worker)
- `tetherto-qvac-sdk>=0.19.0`

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install QVAC SDK globally (Node.js required):
   ```bash
   npm install -g @qvac/sdk@0.19.1
   ```

3. Download models (automatic on first run, but you can pre-download):
   ```bash
   python -m tetherto.qvac_sdk install-worker
   ```

## Usage

```bash
# Via command-line argument
python main.py "Hola mundo"

# Interactive mode
python main.py
```

## How It Works

1. **Registry Inspection**: The app calls `model_registry_list()` to fetch all available models (786+ models)
2. **Model Selection**: Automatically picks instruction/chat models (`gemma`, `qwen`, `salamandrata`) or falls back to any `.gguf` model
3. **Translation**: Uses `loadModel()` and `completion()` to translate text using an LLM
4. **Output**: Streams translation tokens directly to the terminal

No API keys, no cloud usage — everything runs locally on your device.

## Troubleshooting

- **"No models found"**: Install QVAC SDK: `npm install -g @qvac/sdk`
- **"Model not downloaded"**: First run takes a few minutes to download the model automatically
- **"Bare binary not found"**: Set `QVAC_WORKER_PATH` and `QVAC_BARE_PATH` env vars or use `QVAC_SDK_DIR`

## SDK Version

- `tetherto-qvac-sdk`: 0.19.1
- `@qvac/sdk`: 0.19.1
