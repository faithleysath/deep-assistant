import asyncio

class EventManager:
    def __init__(self):
        self.events = asyncio.Queue()
        self.handlers = []

    async def run(self):
        while True:
            event = await self.events.get()
            print(f'Got event: {event}')