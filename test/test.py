import asyncio
import aiohttp
from ..espx.utils import CertificateTemplate

async def test():

    _templates = await CertificateTemplate.get("premium_blackyellow")
    _img  = await _templates.generate(
        name="John Doe",
        eventname="Python Conference 2024",
        organizer="SpruceBot",
        rank=1
    ) if _templates else None
    print(_img)
    

asyncio.run(test())