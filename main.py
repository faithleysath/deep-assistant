import asyncio
from core import EventManager
from models import PrivateMessageEvent
from qqws import listen_message

@EventManager.register()
async def handle_message(event: PrivateMessageEvent):
    print(event.message)

loop = asyncio.get_event_loop()
loop.create_task(listen_message())
loop.create_task(EventManager.run())
loop.run_forever()