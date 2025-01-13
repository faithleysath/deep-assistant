import asyncio
from typing import Type, Optional
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
                event.trigger_num += 1
                result = await handler(event)

    @classmethod
    async def add_event(cls, event: Event):
        if event.status == EventStatus.PENDING:
            if event.trigger_num == 0:
                print(f'Adding immediate event: {event}')
                await cls.immediate_events.put(event)
            else:
                print(f'Adding delayed event: {event}')
                await cls.delayed_events.put(event)

    @classmethod
    def register(cls, event_type: Optional[Type[Event]] = None, priority: int = 0):
        def decorator(handler):
            nonlocal event_type
            if event_type is None:
                event_type = handler.__annotations__['event']
            cls.handlers.append((event_type, handler, priority))
            return handler
        return decorator
