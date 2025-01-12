from ..core import EventManager
import asyncio

async def handle_download(event):
    print(f'[handle_download] Downloading {event.url}...')
