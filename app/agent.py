import json
import logging
from openai import AsyncOpenAI
from app.tools import tool_manager
from app.tools.builtin.memory import Memory, MemoryManager
from app.config import config
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 初始化 OpenAI 客户端
client = AsyncOpenAI(
    api_key=config.get("api_key"),
    base_url=config.get("BASE_URL"),
)

async def send_messages(messages, tools=None):
    """
    发送消息到 LLM 并获取响应。
    """
    if tools is None:
        tools = tool_manager.tools
    
    chat_completion = await client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return chat_completion.choices[0].message

class Agent:
    """基于llm的智能体代理"""
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.memory_manager = MemoryManager(agent_name)
        self.uniform_prompt = ""
        with open(os.path.join(os.path.dirname(__file__), "agents", 'uniform.txt'), "r", encoding='utf-8') as f:
            self.uniform_prompt = f.read()
        self.special_prompts = ""
        with open(os.path.join(os.path.dirname(__file__), "agents", self.agent_name + '.txt'), "r", encoding='utf-8') as f:
            self.special_prompts = f.read()
    
    async def think_once(self, messages_history):
        """思考一个回合"""
        # 构建messages列表，包括自身设定，自身记忆，历史消息
        messages = [
            {"role": "system", "content": self.uniform_prompt},
            {"role": "system", "content": self.special_prompts},
            {"role": "system", "content": self.memory_manager.get_summary()},
        ]
        messages.extend(messages_history)
        # 发送消息并获取响应
        response = await send_messages(messages)
        # 循环处理 LLM 的工具调用
        while response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                logging.warning(f"Calling function: {function_name} with args: {function_args}")
                try:
                    if function_name in tool_manager.exports:
                        tool_result = tool_manager.exports[function_name](**function_args)
                    else:
                        tool_result = {"status": "error", "message": f"Unknown function: {function_name}"}
                except Exception as e:
                    tool_result = {"status": "error", "message": str(e)}
