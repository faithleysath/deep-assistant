import asyncio
from app.core import EventManager
from app.models import PrivateMessageEvent
from app.qqws import listen_message

@EventManager.register()
async def handle_message(event: Priv

loop = asyncio.get_event_loop()
loop.create_task(listen_message())
loop.create_task(EventManager.run())
loop.run_forever()