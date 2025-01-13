import json
import logging
from openai import OpenAI
from datetime import datetime
from typing import Dict, Optional

# 配置日志
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-c5ea9ba45f3f4fdbb55c2d6a32399a57",
    base_url="https://api.deepseek.com",
)

def send_messages(messages, tools={}):
    """
    发送消息到 LLM 并获取响应。
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message


class Memory:
    def __init__(self, key: str, value: str, created: Optional[str] = None, modified: Optional[str] = None):
        """
        初始化记忆对象。
        """
        self.key = key
        self.value = value
        self.created_at = created or datetime.now().isoformat()
        self.modified_at = modified or datetime.now().isoformat()

    def to_dict(self):
        """
        将记忆对象转换为字典格式。
        """
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "modified_at": self.modified_at
        }


class MemoryManager:
    def __init__(self, file_path: str = "memories.json"):
        """
        初始化记忆管理器。
        """
        self.file_path = file_path
        self.memories: Dict[str, Memory] = {}
        self.load_memories()

    def add_or_update_memory(self, key: str, value: str):
        """
        添加或更新记忆。
        """
        if key in self.memories:
            # 更新 existing memory
            self.memories[key].value = value
            self.memories[key].modified = datetime.now().isoformat()
        else:
            # 添加 new memory
            self.memories[key] = Memory(key, value)
        self.save_memories()

    def delete_memory(self, key: str):
        """
        删除记忆。
        """
        if key in self.memories:
            del self.memories[key]
            self.save_memories()
        else:
            raise ValueError(f"Memory with key '{key}' does not exist.")

    def get_summary(self) -> Dict:
        """
        获取记忆概览信息，列出所有记忆。
        """
        return {
            "total_memories": len(self.memories),
            "all_memories": [memory.to_dict() for memory in self.memories.values()]
        }

    def save_memories(self):
        """
        将记忆保存到本地文件。
        """
        memories_data = {key: memory.to_dict() for key, memory in self.memories.items()}
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(memories_data, file, indent=4, ensure_ascii=False)
        logging.info(f"Memories saved to {self.file_path}")

    def load_memories(self):
        """
        从本地文件加载记忆。
        """
        try:
            with open(self.file_path, "r", encoding='utf-8') as file:
                memories_data = json.load(file)
                for key, data in memories_data.items():
                    self.memories[key] = Memory(
                        key=data["key"],
                        value=data["value"],
                        created=data.get("created"),
                        modified=data.get("modified")
                    )
            logging.info(f"Memories loaded from {self.file_path}")
        except FileNotFoundError:
            logging.warning(f"No memory file found at {self.file_path}. Starting with an empty memory manager.")


# 定义工具函数
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_or_update_memory",
            "description": "Add or update a memory in the memory manager.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key associated with the memory."
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to store in memory."
                    }
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_memory",
            "description": "Delete a memory from the memory manager.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key associated with the memory."
                    }
                },
                "required": ["key"]
            }
        }
    }
]


# 初始化记忆管理器
memory_manager = MemoryManager()
prompt = """You are a helpful assistant that can manage memories. You need to actively add useful memories, especially about the user, to be more helpful.

Current time: {current_time}

Your memory is summarized below. It includes:
- Total memories: The total number of memories stored.
- All memories: A list of all memories with their keys, values, creation time, and last modification time.

Here is your current memory summary:
{memory_summary}

**Rules for using tools:**
1. **Add or update memories proactively:**
   - If the user provides new information that is useful for future interactions, call the `add_or_update_memory` tool to store it.

2. **Delete memories when necessary:**
   - If the user requests to delete a memory, call the `delete_memory` tool to remove it.
    - **Outdated Information:** If the memory contains information that is no longer relevant or has become outdated.
    - **Completed Tasks:** If the memory was created for a temporary task or reminder, and that task has been completed.
    - **User Request:** If the user explicitly requests the deletion of a specific memory.
    - **Redundant Data:** If the memory contains redundant or duplicate information that is no longer needed.
    - **Temporary Use:** If the memory was created for a temporary purpose and is no longer required.

3. **Handle errors gracefully:**
   - If a tool call fails (e.g., trying to delete a non-existent key), inform the user and suggest an alternative action.

**Your goal:**
- Use tools efficiently to provide the best possible assistance.
- Avoid redundant tool calls that waste time and resources.
- Always prioritize the user's needs and provide clear, helpful responses."""

# 多轮对话
def chat():
    messages = [
        {"role": "system", "content": "You are a helpful assistant that can manage memories. You need to actively add useful memories, especially about the user, to be more helpful."},
    ]
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # 更新 messages[0] 为当前记忆概览
        memory_summary = memory_manager.get_summary()
        current_time = datetime.now().isoformat()
        messages[0] = {"role": "system", "content": prompt.format(current_time=current_time, memory_summary=json.dumps(memory_summary, indent=4, ensure_ascii=False))}

        # 添加用户输入到消息历史
        messages.append({"role": "user", "content": user_input})

        # 发送消息并获取响应
        response = send_messages(messages, tools=tools)

        # 处理 LLM 的工具调用
        while response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = eval(tool_call.function.arguments)

                logging.warning(f"Calling function: {function_name} with args: {function_args}")

                try:
                    if function_name == "add_or_update_memory":
                        memory_manager.add_or_update_memory(**function_args)
                        tool_result = json.dumps({"status": "success"}, ensure_ascii=False)
                    elif function_name == "delete_memory":
                        memory_manager.delete_memory(**function_args)
                        tool_result = json.dumps({"status": "success"}, ensure_ascii=False)
                    else:
                        tool_result = json.dumps({"status": "error", "message": f"Unknown function: {function_name}"}, ensure_ascii=False)
                except Exception as e:
                    tool_result = json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

                # 将工具调用结果添加到消息历史
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_result})

            # 再次调用 LLM 以处理工具结果
            response = send_messages(messages, tools=tools)

        # 添加 LLM 响应到消息历史
        if response.content:
            print(f"Assistant: {response.content}")
        messages.append(response)

# 启动对话
if __name__ == "__main__":
    chat()