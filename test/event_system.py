from ..core import EventManager
from ..models import DownloadEvent
import asyncio

async def handle_download(event: DownloadEvent):
    print(f'[handle_download] Downloading {event.url}...')
