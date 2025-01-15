import asyncio
import json
import logging
from typing import Any, Dict, Optional
from websockets.client import connect
from websockets.exceptions import ConnectionClosed
from app.core.event_manager import EventManager
from app.models.events import WebSocketEvent

logger = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self, uri: str):
        self.uri = uri
        self.connection = None
        self.running = False

    async def connect(self):
        try:
            self.connection = await connect(self.uri)
            self.running = True
            logger.info(f"Connected to WebSocket server at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            raise

    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            self.running = False
            logger.info("Disconnected from WebSocket server")

    async def send_message(self, message: Dict[str, Any]):
        if not self.connection:
            raise RuntimeError("WebSocket connection not established")
        
        try:
            await self.connection.send(json.dumps(message))
            logger.debug(f"Sent message: {message}")
        except ConnectionClosed:
            logger.error("WebSocket connection closed unexpectedly")
            raise

    async def receive_messages(self):
        while self.running:
            try:
                message = await self.connection.recv()
                logger.debug(f"Received message: {message}")
                
                # Create and dispatch WebSocket event
                event = WebSocketEvent(
                    event_type="websocket_message",
                    data=json.loads(message)
                )
                await EventManager.add_event(event)
                
            except ConnectionClosed:
                logger.error("WebSocket connection closed unexpectedly")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error receiving WebSocket message: {e}")
                self.running = False
                break

    async def run(self):
        await self.connect()
        asyncio.create_task(self.receive_messages())
