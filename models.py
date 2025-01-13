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
        
    @staticmethod
    def from_dict(data: dict):
        segment_type = MessageSegmentType(data.get("type", "unknown"))
        if segment_type == MessageSegmentType.TEXT:
            return TextSegment(data)
        else:
            return UnknownSegment(data)

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
    def __init__(self, message_id: int, user_id: int, message_type: MessageType, timestamp: int, raw_message: str, segments: list[MessageSegment]):
        self.message_id = message_id
        self.user_id = user_id
        self.type = message_type
        self.timestamp = timestamp
        self.raw_message = raw_message
        self.segments = segments

    @staticmethod
    def from_dict(data: dict):
        message_id = data.get("message_id", 0)
        user_id = data.get("user_id", 0)
        message_type = MessageType(data.get("message_type", "private"))
        timestamp = data.get("timestamp", 0)
        raw_message = data.get("raw_message", "")
        segments = [MessageSegment.from_dict(seg) for seg in data.get("message", [])]
        if message_type == MessageType.PRIVATE:
            return PrivateMessage(message_id, user_id, timestamp, raw_message, segments)
        elif message_type == MessageType.GROUP:
            return GroupMessage(message_id, user_id, timestamp, raw_message, segments)

    def __str__(self):
        return f"{self.type.name.capitalize()} message from {self.user_id}: {self.raw_message}"
    
    def __repr__(self):
        return str(self)
    
class PrivateMessage(Message):
    """私聊消息，继承自 Message"""
    def __init__(self, message_id: int, user_id: int, timestamp: int, raw_message: str, segments: list[MessageSegment]):
        super().__init__(message_id, user_id, MessageType.PRIVATE, timestamp, raw_message, segments)

class GroupMessage(Message):
    """群聊消息，继承自 Message"""
    def __init__(self, message_id: int, user_id: int, group_id: int, timestamp: int, raw_message: str, segments: list[MessageSegment]):
        super().__init__(message_id, user_id, MessageType.GROUP, timestamp, raw_message, segments)
        self.group_id = group_id