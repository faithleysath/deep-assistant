import asyncio
from typing import Type
from .models import Event

class EventManager:
    
    events = asyncio.Queue()
    handlers = []

    @classmethod
    async def run(cls):
        while True:
            event = await cls.events.get()
            print(f'Got event: {event}')

    @classmethod
    def register(cls, event_type: Type[Event], priority: int = 0):
        def decorator(handler):
            cls.handlers.append((event_type, handler))
            return handler
        return decorator