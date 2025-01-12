import time
import uuid

class Condition:
    """Condition is a base class for all conditions"""
    pass

class Event:
    def __init__(self, **raw_data):
        self.raw_data = raw_data
        self.time = raw_data.get('time', time.time())
        self.id = raw_data.get('id', uuid.uuid4())