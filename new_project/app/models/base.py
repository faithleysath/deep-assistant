from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime

class EventStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEPRECATED = "deprecated"

class Event:
    def __init__(self, 
                 event_type: str,
                 data: Dict[str, Any],
                 status: EventStatus = EventStatus.PENDING,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.event_type = event_type
        self.data = data
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.trigger_num = 0

    def update_status(self, status: EventStatus):
        self.status = status
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "data": self.data,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "trigger_num": self.trigger_num
        }
