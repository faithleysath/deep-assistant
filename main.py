import asyncio
from core import EventManager
from models import MessageEvent

@EventManager.register
async def handle_message(event: MessageEvent):
    print(event.message)

async def main():
