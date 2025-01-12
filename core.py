import asyncio

class EventManager:
    def __init__(self):
        self.listeners = []
    
    def subscribe(self, listener):
        self.listeners.append(listener)
    
    def notify(self, event):
        for listener in self.listeners:
            listener.notify(event)