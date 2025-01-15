import asyncio
from app.core import EventManager
from app.models import PrivateMessageEvent, UserMessageEvent
from app.qqws import listen_message
from app.config import config
from app.agent import Agent
from app.db import get_messages

@EventManager.register()
async def handle_qq_message(event: PrivateMessageEvent):
    message = event.message
    if message.user_id == config.get("user_id"):
        return
    
@EventManager.register()
async def handle_user_message(event: UserMessageEvent):
    agent = Agent("deepAssistant")

loop = asyncio.get_event_loop()
loop.create_task(listen_message())
loop.create_task(EventManager.run())
loop.run_forever()