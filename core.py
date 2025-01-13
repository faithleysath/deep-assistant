import asyncio
from typing import Type
from models import Event, EventStatus

loop = asyncio.get_event_loop()

class EventManager:
    
    immediate_events = asyncio.Queue() # events with high priority
    delayed_events = asyncio.Queue() # events with low priority
    handlers = []

    @classmethod
    async def run(cls):
        loop.create_task(cls.run_immediate())
        loop.create_task(cls.run_delayed())

    @classmethod
    async def run_immediate(cls):
        while True:
            event = await cls.immediate_events.get()
            loop.create_task(cls.handle_event(event))
    
    @classmethod
    async def run_delayed(cls):
        while True:
            event = await cls.delayed_events.get()
            loop.create_task(cls.handle_event(event))
            await asyncio.sleep(0.1) # sleep for a short time to prevent busy waiting

    @classmethod
    async def handle_event(cls, event: Event):
        for event_type, handler, priority in sorted(cls.handlers, key=lambda x: x[2]):
            if isinstance(event, event_type) and event.status != EventStatus.DEPRECATED:
                result = await handler(event)
                if result:
                    event.status = EventStatus.COMPLETE
                else:

    @classmethod
    async def add_event(cls, event: Event):
        if event.status == EventStatus.PENDING:
            if event.trigger_num < 1:
                await cls.immediate_events.put(event)
            else:
                await cls.delayed_events.put(event)

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