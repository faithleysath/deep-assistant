from core import EventManager
from models import DownloadEvent
import asyncio

@EventManager.register()
async def handle_download(event: DownloadEvent):
    print(f'[handle_download] Downloading {event.url}...')
    await asyncio.sleep(10)
    print(f'[handle_download] Downloaded {event.url} to {event.path}')

async def get_user_input(prompt: str) -> str:
    # 在单独的线程中运行 input() 以避免阻塞事件循环
    return await asyncio.to_thread(input, prompt)

async def main():
    while True:
        # read from user input
        url = await get_user_input('Enter URL: ')
        path = await get_user_input('Enter path: ')
        event = DownloadEvent(url=url, path=path)
        await EventManager.events.put(event)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(EventManager.run())
    loop.run_until_complete(main())