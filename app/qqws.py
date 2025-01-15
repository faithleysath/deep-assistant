import websockets
import json
from app.models import Message, MessageEvent
from app.core import EventManager
from app.db import save_message
from app.config import config

# WebSocket 客户端逻辑
async def listen_message():
    # 连接到 WebSocket 服务器
    async with websockets.connect(config.get("WS_URL")) as websocket:
        print(f"已连接到 WebSocket 服务器 {config.get("WS_URL")}")

        # 持续接收消息并输出
        try:
            while True:
                message = await websocket.recv()  # 接收消息
                data: dict = json.loads(message)
                if data.get("post_type", "null") in ("message", "message_sent"):
                    # 保存消息到数据库
                    save_message(
                        message_id=str(data.get("message_id")),
                        user_id=str(data.get("user_id")),
                        type=data.get("message_type"),
                        timestamp=int(data.get("time")),
                        raw_message=data.get("raw_message", ""),
                        data=message
                    )
                    message = Message.from_dict(data)
                    event = MessageEvent.from_message(message)
                    await EventManager.add_event(event)
                    
        except websockets.ConnectionClosed:
            print("连接已关闭")
