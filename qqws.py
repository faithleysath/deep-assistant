import websockets
import json
from models import Message, MessageEvent

# WebSocket 客户端逻辑
async def listen_message():
    # 连接到 WebSocket 服务器
    async with websockets.connect("ws://192.168.137.199:3001/") as websocket:
        print("已连接到 WebSocket 服务器 ws://192.168.137.199:3001/")

        # 持续接收消息并输出
        try:
            while True:
                message = await websocket.recv()  # 接收消息
                data: dict = json.loads(message)
                if data.get("post_type", "null") == "message":
                    message = Message.from_dict(data)
                    event = 
        except websockets.ConnectionClosed:
            print("连接已关闭")
