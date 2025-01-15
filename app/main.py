import asyncio
from app.core import EventManager
from app.models import PrivateMessageEvent
from app.qqws import listen_message
from app.config import config

@EventManager.register()
async def handle_message(event: PrivateMessageEvent):
    message = event.message
    if message.user_id == config.get("user_id"):
        print("来自用户的消息", message.raw_message)

loop = asyncio.get_event_loop()
loop.create_task(listen_message())
loop.create_task(EventManager.run())
loop.run_forever()