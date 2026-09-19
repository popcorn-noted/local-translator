# Local Translator (Spanish → English)

A simple CLI app that uses QVAC to translate Spanish text to English entirely on-device.

## Requirements

- Node.js 18+

## Installation

```bash
npm install
```

## Usage

```bash
# Via command-line argument
node index.js "Hola, ¿cómo estás?"

# Interactive mode
node index.js
```

## How It Works

1. The app loads the QVAC translation model via `loadModel()`
2. It accepts Spanish text via CLI argument or stdin
3. It calls `translate()` to translate to English
4. The translation is printed to stdout

No API keys, no cloud usage — everything runs locally on your device.

## SDK Version

- `@qvac/sdk`: 0.19.1
