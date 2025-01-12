from ..core import EventManager
from ..models import DownloadEvent
import asyncio

async def handle_download(event: DownloadEvent):
    print(f'[handle_download] Downloading {event.url}...')
    await asyncio.sleep(10)
    print(f'[handle_download] Downloaded {event.url} to {event.path}')