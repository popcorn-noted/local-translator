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
            
            # 1. Exact Registry Inspection & Extraction
            print("Fetching model registry...")
            models = await model_registry_list(transport)
            print(f"Found {len(models)} models in registry")
            
            # Extract all .gguf model filenames
            gguf_models = []
            for item in models:
                # Try different property names that might contain the model ID
                model_id = None
                for attr in ['model_id', 'id', 'name', 'filename']:
                    if hasattr(item, attr):
                        model_id = getattr(item, attr)
                        break
                
                if model_id and isinstance(model_id, str) and model_id.endswith('.gguf'):
                    gguf_models.append(model_id)
            
            print(f"Found {len(gguf_models)} .gguf models")
            
            # 2. Model Auto-Selection Logic
            # Priority 1: Instruction/chat models
            priority_keywords = ['gemma', 'salamandrata', 'qwen', 'inst', 'instruct']
            selected_model = None
            
            for model in gguf_models:
                model_lower = model.lower()
                if any(kw in model_lower for kw in priority_keywords):
                    selected_model = model
                    break
            
            # Priority 2: Fall back to any .gguf model
            if not selected_model and gguf_models:
                selected_model = gguf_models[0]
            
            if not selected_model:
                print("No .gguf model found. Please install QVAC models.")
                return
            
            print(f"\nSelected model: {selected_model}")
            
            # 3. SDK Invocation & Async Handling
            try:
                model_id = await load_model(
                    transport, 
                    model_src=selected_model, 
                    model_type="llamacpp-completion"
                )
                print(f"Model loaded successfully: {model_id}")
                
                # Create translation prompt
                prompt = f"Translate to English: {text}"
                
                # Call completion - returns an async iterator
                result = completion(
                    transport, 
                    model_id=model_id, 
                    history=[{"role": "user", "content": prompt}]
                )
                
                # Stream the response
                print(f"\nTranslation:")
                async for token in result.token_stream:
                    print(token, end='', flush=True)
                print()
                
            except Exception as e:
                print(f"\nError loading or using model: {e}")
    
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nMake sure:")
        print("  1. Node.js 18+ is installed")
        print("  2. QVAC SDK is installed globally: npm install -g @qvac/sdk")
        print("  3. Models are downloaded automatically on first run")

if __name__ == "__main__":
    asyncio.run(main())
