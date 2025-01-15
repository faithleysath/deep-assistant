from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

class MemoryItem(BaseModel):
    key: str
    value: Dict
    timestamp: datetime
    metadata: Optional[Dict] = None

class MemoryQuery(BaseModel):
    key: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: Optional[int] = 100

class MemoryResponse(BaseModel):
    key: str
    items: List[MemoryItem]
    total_count: int
