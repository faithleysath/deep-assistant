import json
import logging
from openai import OpenAI
from app.tools import tool_manager
from app.tools.builtin.memory import Memory, MemoryManager
from app.config import config
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=config.get("api_key"),
    base_url=config.get("BASE_URL"),
)

async def send_messages(messages, tools=None):
    """
    发送消息到 LLM 并获取响应。
    """
    if tools is None:
        tools = tool_manager.tools
    
    response = await client.chat.completions.create_async(
        model="deepseek-chat", 
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

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


# 多轮对话
async def chat():
    messages = [
        {"role": "system", "content": "You are a helpful assistant that can manage memories. You need to actively add useful memories, especially about the user, to be more helpful."},
    ]
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        user_input = "Please remember new information about me if needed. If you remember anything, don't tell me what you just remember, just reply me." + user_input
        # 更新 messages[0] 为当前记忆概览
        memory_summary = memory_manager.get_summary()
        current_time = datetime.now().isoformat()
        messages[0] = {"role": "system", "content": prompt.format(current_time=current_time, memory_summary=json.dumps(memory_summary, indent=4, ensure_ascii=False))}

        # 添加用户输入到消息历史
        messages.append({"role": "user", "content": user_input})

        # 发送消息并获取响应
        response = await send_messages(messages, tools=tools)

        # 处理 LLM 的工具调用
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
