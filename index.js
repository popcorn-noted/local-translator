const { Client, loadModel, translate } = require('@qvac/sdk');

async function main() {
    const args = process.argv.slice(2);
    const text = args.length > 0 ? args.join(' ') : '';
    
    if (!text) {
        console.log('Enter Spanish text to translate:');
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        await new Promise(resolve => rl.question('', (answer) => {
            processTranslation(answer);
            rl.close();
        }));
    } else {
        await processTranslation(text);
    }
}

async function processTranslation(text) {
    try {
        const client = new Client();
        await client.connect();
        const { transport } = client;
        
        const modelId = await loadModel(transport, { modelSrc: 'model.esen.intgemm.alphas.bin', modelType: 'nmtcpp-translation' });
        const result = await translate(transport, { modelId, text, modelType: 'nmtcpp-translation', to: 'en', from: 'es' });
        const translation = await result.text;
        console.log(translation);
        
        client.close();
    } catch (error) {
        console.error('Error:', error.message);
        console.error('Tip: Make sure QVAC worker is running');
    }
}

main();
