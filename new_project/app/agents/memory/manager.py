import asyncio
from typing import Dict, List, Optional
from app.core.event_manager import EventManager
from app.models.base import Event
from app.agents.base_agent import BaseAgent

class MemoryManager(BaseAgent):
    def __init__(self, agent_id: str = "memory_manager", config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.memory_store: Dict[str, List[Dict]] = {}
        self.lock = asyncio.Lock()

    async def store_memory(self, key: str, data: Dict) -> None:
        """Store memory data with a specific key"""
        async with self.lock:
            if key not in self.memory_store:
                self.memory_store[key] = []
            self.memory_store[key].append(data)

    async def retrieve_memory(self, key: str) -> Optional[List[Dict]]:
        """Retrieve memory data by key"""
        async with self.lock:
            return self.memory_store.get(key, None)

    async def clear_memory(self, key: str) -> None:
        """Clear memory data by key"""
        async with self.lock:
            if key in self.memory_store:
                del self.memory_store[key]

    async def handle_event(self, event: Event) -> None:
        """Handle memory-related events"""
        if event.event_type == "store_memory":
            await self.store_memory(
                event.data["key"],
                event.data["data"]
            )
        elif event.event_type == "retrieve_memory":
            memory_data = await self.retrieve_memory(event.data["key"])
            await self.send_event(
                "memory_retrieved",
                {"key": event.data["key"], "data": memory_data}
            )
        elif event.event_type == "clear_memory":
            await self.clear_memory(event.data["key"])

    async def process(self) -> None:
        """Main processing loop for memory management"""
        await asyncio.sleep(1)  # Reduce CPU usage
