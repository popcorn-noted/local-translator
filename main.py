import sys
import asyncio
from tetherto.qvac_sdk import Client, load_model, completion, model_registry_list, download_asset

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
            
            # 1. Exact Registry Inspection
            print("Fetching model registry...")
            models = await model_registry_list(transport)
            print(f"Found {len(models)} models")
            
            # Extract .gguf models
            gguf_models = []
            for item in models:
                model_id = None
                registry_path = None
                
                for attr in ['model_id', 'id', 'name']:
                    if hasattr(item, attr):
                        model_id = getattr(item, attr)
                        break
                
                if hasattr(item, 'registryPath'):
                    registry_path = getattr(item, 'registryPath')
                
                if model_id and isinstance(model_id, str) and model_id.endswith('.gguf'):
                    gguf_models.append({
                        'id': model_id,
                        'path': registry_path
                    })
            
            print(f"Found {len(gguf_models)} .gguf models")
            
            # 2. Model Auto-Selection
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
            
            # 3. SDK Invocation
            print("Loading model (this may take a few minutes on first run)...")
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
                msg = str(e).lower()
                if "not found" in msg or "invalid" in msg:
                    print("\nModel not found locally. Downloading...")
                    # Try to download first
                    if selected['path']:
                        await download_asset(transport, selected['path'])
                        print("Download complete. Retrying...")
                        
                        # Try loading again
                        model_id = await load_model(
                            transport, 
                            model_src=selected['id'], 
                            model_type="llamacpp-completion"
                        )
                        print(f"Model loaded: {model_id}")
                    else:
                        print("You need to download the model manually:")
                        print(f"  python -m tetherto.qvac_sdk download-model {selected['id']}")
                else:
                    print(f"\nError: {e}")
    
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nMake sure:")
        print("  1. Node.js 18+ is installed")
        print("  2. QVAC SDK is installed: npm install -g @qvac/sdk")
        print("  3. Run: python -m tetherto.qvac_sdk install-worker")

if __name__ == "__main__":
    asyncio.run(main())
