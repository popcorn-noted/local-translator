const { loadModel, completion, modelRegistryList, modelRegistrySearch, close } = require('@qvac/sdk');

async function main() {
    const text = process.argv[2] || 'Hola mundo';
    console.log('=== QVAC Local Translator ===');
    console.log('Text:', text);
    console.log('');
    
    try {
        // Search for a locally available model
        const models = await modelRegistrySearch({ engine: 'llamacpp-completion' });
        console.log(`Found ${models.length} LLM models`);
        
        // Look for a model that might be available
        const preferredModels = [
            'salamandrata_2b_inst_q4',
            'Qwen3-0.6B',
            'Llama-3.2-1B'
        ];
        
        let model = models.find(m => 
            preferredModels.some(p => (m.modelId || '').includes(p))
        );
        
        if (!model && models.length > 0) {
            model = models[0];
        }
        
        if (!model) {
            console.log('No LLM model available.');
            console.log('Install QVAC: npm install -g @qvac/sdk');
            close();
            return;
        }
        
        console.log('Model:', model.modelId);
        console.log('Engine:', model.engine);
        
        // Try to load the model
        try {
            const modelId = await loadModel({ 
                modelSrc: model.modelId, 
                modelType: model.engine 
            });
            
            console.log('Model loaded:', modelId);
            console.log('');
            console.log('Translation (using LLM):');
            
            const result = completion({ 
                modelId, 
                history: [{ role: 'user', content: `Translate to English: ${text}` }] 
            });
            
            for await (const token of result.tokenStream) {
                process.stdout.write(token);
            }
            console.log();
            
        } catch (loadError) {
            console.log('Model not downloaded yet.');
            console.log('The SDK needs to download the model first (may take a few minutes).');
            console.log('');
            console.log('For immediate results, install translation models:');
            console.log('  npm install -g @qvac/sdk');
        }
        
    } catch (error) {
        console.log('Error:', error.message);
        console.log('');
        console.log('Troubleshooting:');
        console.log('1. Install Node.js 18+ if not installed');
        console.log('2. Run: npm install -g @qvac/sdk');
        console.log('3. Wait for models to download');
    }
    
    close();
}

main();
