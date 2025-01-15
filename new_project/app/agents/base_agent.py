import logging
from typing import Any, Dict, Optional
from app.core.event_manager import EventManager
from app.models.base import Event

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.config = config or {}
        self.running = False

    async def start(self):
        """Start the agent's main loop"""
        self.running = True
        logger.info(f"Agent {self.agent_id} started")

    async def stop(self):
        """Stop the agent's main loop"""
        self.running = False
        logger.info(f"Agent {self.agent_id} stopped")

    async def handle_event(self, event: Event):
        """Handle incoming events"""
        raise NotImplementedError("Subclasses must implement handle_event")

    async def send_event(self, event_type: str, data: Dict[str, Any]):
        """Send an event to the event manager"""
        event = Event(event_type=event_type, data=data)
        await EventManager.add_event(event)
        logger.debug(f"Agent {self.agent_id} sent event: {event_type}")

    async def run(self):
        """Main agent loop"""
        await self.start()
        while self.running:
            try:
                await self.process()
            except Exception as e:
                logger.error(f"Agent {self.agent_id} error: {e}")
                await self.stop()
                raise

    async def process(self):
        """Process logic to be executed in the main loop"""
        raise NotImplementedError("Subclasses must implement process")
