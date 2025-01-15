from datetime import datetime
from typing import Any, Dict
from app.models.base import Event, EventStatus

class WebSocketEvent(Event):
    def __init__(self,
                 event_type: str,
                 data: Dict[str, Any],
                 status: EventStatus = EventStatus.PENDING,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        super().__init__(
            event_type=event_type,
            data=data,
            status=status,
            created_at=created_at,
            updated_at=updated_at
        )

    def validate(self) -> bool:
        """Validate WebSocket event data"""
        required_fields = ["message_id", "user_id", "type", "timestamp"]
        return all(field in self.data for field in required_fields)
