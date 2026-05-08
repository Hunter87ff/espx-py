import asyncio
from espx.client import ESPXClient



async def test(): 
    client = ESPXClient(base_url="http://localhost:8001", access_token="sprucepointtable87")
    _templates = await client.leaderboards.br.list_templates()
    print("Available Templates:")
    for template in _templates:
        print(f"- {template.name} (ID: {template.id})")


asyncio.run(test())