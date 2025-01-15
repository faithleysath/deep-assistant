import asyncio
import logging
from app.agent import Agent

async def test_think_once():
    # 设置日志级别为DEBUG
    logging.basicConfig(level=logging.DEBUG)
    
    # 创建一个测试agent
    agent = Agent("test_agent")
    
    # 准备测试消息历史
    messages_history = [
        {"role": "user", "content": "你好"}
    ]
    
    # 调用think_once方法
    response = await agent.think_once(messages_history)
    print("LLM Response:", response)

if __name__ == "__main__":
    asyncio.run(test_think_once())
