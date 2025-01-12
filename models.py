import time
import uuid
import datetime

class Condition:
    """Condition is a base class for all conditions"""
    pass

class Event:
    """Event is a base class for all events"""
    def __init__(self, **raw_data):
        self.raw_data = raw_data
        self.time = raw_data.get('time', time.time())
        self.id = raw_data.get('id', uuid.uuid4())
        self.status = raw_data.get('status', 'pending')
        self.name = raw_data.get('name', 'untitled')
        self.summary = raw_data.get('summary', 'no summary')

    def __str__(self):
        return f'{}