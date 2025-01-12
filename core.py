import asyncio

class EventManager:
    
    events = asyncio.Queue()
    handlers = []

    @classmethod
    async def run(cls):
        while True:
            event = await cls.events.get()
            print(f'Got event: {event}')
