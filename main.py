import sys
import asyncio
from tetherto.qvac_sdk import Client, load_model, completion, model_registry_list

async def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Enter text to translate (empty line to exit):")
        text = sys.stdin.readline().strip()

    if not text:
        return

    try:
        async with Client() as client:
            transport = client.transport
            # List available models
            models = await model_registry_list(transport)
            print(f"Found {len(models)} models in registry")
            
            # Use LLM-based translation
            model_id = await load_model(transport, model_src="Qwen3-0.6B-Q4_0", model_type="llamacpp-completion")
            print(f"Model loaded: {model_id}")
            
            prompt = f"Translate to English: {text}"
            result = completion(transport, model_id=model_id, history=[{"role": "user", "content": prompt}])
            print(result)
            
    except Exception as e:
        print(f"Error: {e}")
        print("Tip: Download model first: python -m tetherto.qvac_sdk download-model Qwen3-0.6B-Q4_0")

if __name__ == "__main__":
    asyncio.run(main())
