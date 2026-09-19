import asyncio
from tetherto.qvac_sdk import Client, model_registry_list

async def test():
    async with Client() as c:
        models = await model_registry_list(c.transport)
        for m in models:
            model_id = getattr(m, 'model_id', str(m))
            if 'en' in model_id.lower():
                print(model_id)

asyncio.run(test())
