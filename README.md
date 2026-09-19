# Local Translator (Spanish → English)

A simple CLI app that uses QVAC to translate text entirely on-device.

## Requirements

- Node.js 18+
- RAM: 4GB+ (for model loading)

## Installation

```bash
npm install
```

## First-Time Setup

Models need to be downloaded on first run. This may take a few minutes:

```bash
node index.js
```

## Usage

```bash
# Via command-line argument
node index.js "Hola mundo"

# Interactive (prompts for text)
node index.js
```

## How It Works

1. The app uses QVAC's `modelRegistryList()` to find available LLM models
2. Downloads the model if not already present (first run only)
3. Uses `loadModel()` to load the model into memory
4. Calls `completion()` to translate the text to English
5. Prints the translation

No API keys, no cloud usage — everything runs locally on your device.

## SDK Version

- `@qvac/sdk`: 0.19.1
