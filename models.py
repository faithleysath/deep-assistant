from enum import Enum
import time
from typing import Optional
import uuid
import datetime


class Condition:
    """Condition is a base class for all conditions"""

    pass


class EventStatus(Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    DEPRECATED = "deprecated"


class Event:
    """Event is a base class for all events"""

    def __init__(
        self,
        timestamp: Optional[float] = None,
        id: Optional[uuid.UUID] = None,
        status: EventStatus = EventStatus.PENDING,
        trigger_num: int = 0,
        name: str = "untitled",
        summary: str = "no summary",
        creator: str = "unknown",
        source: str = "unknown",
        **raw_data,
    ):
        self.raw_data = raw_data
        self.time = timestamp if timestamp is not None else time.time()
        self.id = id if id is not None else uuid.uuid4()
        self.status = status
        self.trigger_num = trigger_num
        self.name = name
        self.summary = summary
        self.creator = creator
        self.source = source

    def __str__(self):
        return (
            f"{datetime.datetime.fromtimestamp(self.time)}: {self.name} ({self.status})"
        )

    def __repr__(self):
        return str(self)


class DownloadEvent(Event):
    def __init__(self, url: str, path: str, **raw_data):
        super().__init__(**raw_data)
        self.url = url
        self.path = path


class MessageSegmentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "record"
    FILE = "file"
    REPLY = "reply"
    FACE = "face"
    AT = "at"
    UNKNOWN = "unknown"

class MessageType(Enum):
    PRIVATE = "private"
    GROUP = "group"

class MessageSegment:
    """基类，用于表示消息片段的通用部分"""
    def __init__(self, raw_data: dict):
        self.type = self._determine_type(raw_data)  # 根据传入数据确定类型
        self.data = raw_data.get("data", {})  # 通用数据

    @staticmethod
    def _determine_type(raw_data: dict) -> MessageSegmentType:
        try:
            return MessageSegmentType(raw_data.get("type", "unknown"))
        except ValueError:
            return MessageSegmentType.UNKNOWN

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return str(self)
    
class TextSegment(MessageSegment):
    """文本片段，继承自 MessageSegment"""
    def __init__(self, raw_data: dict):
        super().__init__(raw_data)
        self.content: str = self.data.get("text", "")

    def __init__(self, content: str):
        self.__init__({"type": "text", "data": {"text": content}})

    def __str__(self):
        return self.content
    
class UnknownSegment(MessageSegment):
    """未知片段，继承自 MessageSegment"""
    def __init__(self, raw_data: dict):
        super().__init__(raw_data)
        self.type = MessageSegmentType.UNKNOWN

    def __str__(self):
        return "<UNKNOWN SEGMENT>"

class Message:
    """消息类，用于表示消息的通用部分"""
    def __init__(self, message_id: int, user_id: int, message_type: MessageType, timestamp: int, raw_data: dict):
        self.message_id = message_id
        self.user_id = user_id
        self.type = message_type
        self.raw_data = raw_data
        self.timestamp = timestamp
        self.segments = self._parse_segments(raw_data.get("message", ""))

    def _parse_segments(self, message: str) -> list[MessageSegment]:
        segments = []
        for seg in message:
            if seg["type"] == "text":
                segments.append(TextSegment(seg))
            else:
                segments.append(UnknownSegment(seg))
        return segments

    def __str__(self):
        return f"{self.type.name.capitalize()} message from {self.user_id}: {''.join([str(seg) for seg in self.segments])}"

    def __repr__(self):
        return str(self)