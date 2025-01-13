import asyncio
from core import EventManager
from models import MessageEvent
from qqws import listen_message

@EventManager.register
async def handle_message(event: MessageEvent):
    print(event.message)

loop = asyncio.get_event_loop()
loop.create_task(listen_message())
loop.create_task(EventManager.run())
loop.run_forever()