from enum import Enum
import time
from typing import Optional
import uuid
import datetime

class Condition:
    """Condition is a base class for all conditions"""
    pass

class EventStatus(Enum):
    PENDING = 'pending'
    COMPLETE = 'complete'
    DEPRECATED = 'deprecated'

class Event:
    """Event is a base class for all events"""
    def __init__(self, time: Optional[float] = None, id: Optional[uuid.UUID] = None, status: EventStatus = EventStatus.PENDING, trigger_num: int = 0, name: str = 'untitled', summary: str = 'no summary', creator: str = 'unknown', source: str = 'unknown', **raw_data):
        self.raw_data = raw_data
        self.time = time if time is not None else time.time()
        self.id = id if id is not None else uuid.uuid4()
        self.status = status
        self.trigger_num = trigger_num
        self.name = name
        self.summary = summary
        self.creator = creator
        self.source = source

    def __str__(self):
        return f'{datetime.datetime.fromtimestamp(self.time)}: {self.name} ({self.status})'

    def __repr__(self):
        return str(self)

class DownloadEvent(Event):
    def __init__(self, **raw_data):
        super().__init__(**raw_data)
        self.path = raw_data.get('path', 'unknown')
        self.url = raw_data.get('url', 'unknown')
        if self.path == 'unknown' or self.url == 'unknown':
            self.status = EventStatus.DEPRECATED
