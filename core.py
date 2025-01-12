import asyncio
from typing import Type
from models import Event

loop = asyncio.get_event_loop()

class EventManager:
    
    immediate_events = asyncio.Queue()
    delayed_events = asyncio.Queue()
    handlers = []

    @classmethod
    async def run(cls):
        while True:
            event = await cls.events.get()
            print(f'[EventManager] Got event: {event}')

    @classmethod
    async def run_immediate(cls):
            while True:
                event = await cls.immediate_events.get()
                await cls.execute_event(event)

    @classmethod
    async def execute_event(cls, event: Event):
        for event_type, handler, priority in sorted(cls.handlers, key=lambda x: x[2]):
            if isinstance(event, event_type):
                

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