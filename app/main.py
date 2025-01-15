import asyncio
from typing import List
from app.core import EventManager
from app.models import PrivateMessageEvent, UserMessageEvent, Message
from app.qqws import listen_message, send_private_msg
from app.config import config
from app.agent import Agent
from app.db import get_messages

def get_openai_messages(messages: List[Message]):
    results = []
    for msg in messages:
        if msg.user_id == config.get("assistant_id"):
            results.append({"role": "assistant", "content": msg.raw_message})
        elif msg.user_id == config.get("user_id"):
            results.append({"role": "user", "content": msg.raw_message})
    return results

@EventManager.register()
async def handle_qq_message(event: PrivateMessageEvent):
    message = event.message
    if message.user_id == config.get("user_id"):
        await EventManager.add_event(UserMessageEvent())
    
@EventManager.register()
async def handle_user_message(event: UserMessageEvent):
    agent = Agent("deepAssistant")
    messages = get_messages(uids=[config.get("user_id"), config.get("assistant_id")], types=["private"])
    openai_messages = get_openai_messages(messages)
    response = await agent.think_once(openai_messages)
    await send_private_msg(config.get("user_id"), response)

loop = asyncio.get_event_loop()
loop.create_task(listen_message())
loop.create_task(EventManager.run())
loop.run_forever()