import sys
import asyncio
from tetherto.qvac_sdk import Client, load_model, completion, model_registry_list

async def main():
    # CLI input handling
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Enter text to translate (or press Enter to quit):")
        text = sys.stdin.readline().strip()
    
    if not text:
        return
    
    try:
        async with Client() as client:
            transport = client.transport
            
            print("Fetching model registry...")
            models = await model_registry_list(transport)
            print(f"Found {len(models)} models in registry")
            
            # Extract .gguf models with full details
            gguf_models = []
            for item in models:
                model_id = None
                registry_path = None
                registry_source = None
                
                for attr in ['model_id', 'id', 'name']:
                    if hasattr(item, attr):
                        model_id = getattr(item, attr)
                        break
                
                if hasattr(item, 'registryPath'):
                    registry_path = getattr(item, 'registryPath')
                if hasattr(item, 'registrySource'):
                    registry_source = getattr(item, 'registrySource')
                
                if model_id and isinstance(model_id, str) and model_id.endswith('.gguf'):
                    gguf_models.append({
                        'id': model_id,
                        'path': registry_path,
                        'source': registry_source
                    })
            
            print(f"Found {len(gguf_models)} .gguf models")
            
            # Find models that match local availability
            priority_keywords = ['llama', 'gemma', 'salamandrata', 'qwen', 'inst', 'instruct']
            selected = None
            
            for model in gguf_models:
                if any(kw in model['id'].lower() for kw in priority_keywords):
                    selected = model
                    break
            
            if not selected and gguf_models:
                selected = gguf_models[0]
            
            if not selected:
                print("No .gguf model found.")
                return
            
            print(f"\nSelected model: {selected['id']}")
            
            # The model needs to be downloaded locally first
            print(f"\nThis model needs to be downloaded locally.")
            print("First run may take several minutes to download the model.")
            print(f"Try loading with: {selected['id']}")
            
            # Try loading with model ID
            try:
                model_id = await load_model(
                    transport, 
                    model_src=selected['id'], 
                    model_type="llamacpp-completion"
                )
                print(f"Model loaded: {model_id}")
                
                prompt = f"Translate to English: {text}"
                result = completion(
                    transport, 
                    model_id=model_id, 
                    history=[{"role": "user", "content": prompt}]
                )
                
                print(f"\nTranslation:")
                async for token in result.token_stream:
                    print(token, end='', flush=True)
                print()
                
            except Exception as e:
                msg = str(e)
                if "not found" in msg.lower():
                    print("\nModel not found locally.")
                    print("You need to download the model first:")
                    print("  python -m tetherto.qvac_sdk download-model <model-name>")
                    print("\nOr wait for automatic download on first run.")
                else:
                    print(f"\nModel error: {e}")
    
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nMake sure:")
        print("  1. Node.js 18+ is installed")
        print("  2. QVAC SDK is installed: npm install -g @qvac/sdk")
        print("  3. Run: python -m tetherto.qvac_sdk install-worker")

if __name__ == "__main__":
    asyncio.run(main())
