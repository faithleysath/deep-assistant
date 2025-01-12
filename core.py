import asyncio

class EventManager:
    def __init__(self):
        self.events = asyncio.Queue()
        self.handlers = []