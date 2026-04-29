import asyncio
import sys
# add paths
sys.path.insert(0, "/Users/francois-jeandazin/AETHERFLOW")
sys.path.insert(0, "/Users/francois-jeandazin/AETHERFLOW/Frontend/3. STENCILER")

from routers.design_token_extractor import extract_tokens_background

async def main():
    await extract_tokens_background("dnmade1-2026-blart-samuel")

asyncio.run(main())
