import asyncio

class EventManager:
    def __init__(self):
        self.listeners = asyncio.Queue()