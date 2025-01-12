from ..core import EventManager
from ..models import DownloadEvent
import asyncio

@EventManager.register()
async def handle_download(event: DownloadEvent):
    print(f'[handle_download] Downloading {event.url}...')
    await asyncio.sleep(10)
    print(f'[handle_download] Downloaded {event.url} to {event.path}')

async def main():
    while True:
        # read from user input
        url = input('Enter URL: ')
        path = input('Enter path: ')
        event = DownloadEvent(url=url, path=path)
        await EventManager.events.put(event)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(EventManager.run())
    loop.run_until_complete(main())