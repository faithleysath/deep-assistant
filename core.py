import asyncio

class EventManager:
    
    events = asyncio.Queue()
    handlers = []

    @staticmethod
    async def run(self):
        while True:
            event = await self.events.get()
            print(f'Got event: {event}')
