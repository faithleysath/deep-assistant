from ..core import EventManager


async def handle_download(event):
    print(f'[handle_download] Downloading {event.url}...')
