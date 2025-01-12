import asyncio
from typing import Type
from models import Event

loop = asyncio.get_event_loop()

class EventManager:
    
    events = asyncio.Queue()
    handlers = []

    @classmethod
    async def run(cls):
        while True:
            event = await cls.events.get()
            print(f'[EventManager] Got event: {event}')
            for event_type, handler, priority in sorted(cls.handlers, key=lambda x: x[2]):
                if isinstance(event, event_type):
                    loop.create_task(handler(event))
                    print(f'[EventManager] Dispatched event: {event} to {handler}')

    @classmethod
    def register(cls, event_type: Type[Event], priority: int = 0):
        def decorator(handler):
            cls.handlers.append((event_type, handler, priority))
            return handler
        return decorator
    
    @classmethod
    def register(cls, priority: int = 0):
        def decorator(handler):
            # read the event type from the handler annotation
            event_type = handler.__annotations__['event']
            cls.handlers.append((event_type, handler, priority))
        return decorator