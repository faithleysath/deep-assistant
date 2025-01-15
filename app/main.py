import asyncio
from app.core import EventManager
from app.models import PrivateMessageEvent
from app.qqws import listen_message
from app.config import config

@EventManager.register()
async def handle_qq_message(event: PrivateMessageEvent):
    message = event.message
    if message.user_id == config.get("user_id"):
        return
    
@EventManager.register()
async def handle_group_message(event: PrivateMessageEvent):
    message = event.message
    if message.user_id == config.get("user_id"):
        return
    if message.raw_message == "你好":
        await event.reply("你好呀！")

loop = asyncio.get_event_loop()
loop.create_task(listen_message())
loop.create_task(EventManager.run())
loop.run_forever()