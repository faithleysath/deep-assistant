import aiohttp
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


def send_private_msg(user_id: int, message: str) -> dict:
    """
    发送私聊消息
    
    Args:
        user_id: 接收者QQ号
        message: 消息内容字符串
        
    Returns:
        API响应结果
    """
    url = config.get("HTTP_URL") + "/send_private_msg"
    payload = {
        "user_id": user_id,
        "message": [
            {
                "type": "text",
                "data": {
                    "text": message
                }
            }
        ]
    }
    response = requests.post(url, json=payload)
    return response.json()
