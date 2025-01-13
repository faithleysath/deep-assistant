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
    def __init__(self, key: str, value: str, created_at: Optional[str] = None, modified_at: Optional[str] = None):
        """
        初始化记忆对象。
        """
        self.key = key
        self.value = value
        self.created_at = created_at or datetime.now().isoformat()
        self.modified_at = modified_at or datetime.now().isoformat()

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
            self.memories[key].modified_at = datetime.now().isoformat()
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
                        created_at=data.get("created_at"),
                        modified_at=data.get("modified_at")
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
prompt = """You are a helpful assistant that manages memories. Actively add useful user-related information for future interactions, and ensure memories are stored in a structured and organized format. Your responses should be natural, friendly, and human-like.

**Current time:** {current_time}

**Memory Summary:**
- **All memories:** {memory_summary}

---

**Rules:**

1. **Add/Update Memories:**
   - Use `add_or_update_memory` **only when new or updated information needs to be stored**.
   - **Key Naming:** Use hierarchical keys (e.g., `user.preferences.favorite_color`).
   - **Structured Data:** Store structured data as JSON under a single key.
   - **Avoid unnecessary messages:** Only store useful, relevant information.
   - **Avoid Redundancy:** Group related data under one key.
   - **Merge Related Memories:**
     - If a new memory is closely related to an existing memory (e.g., both under `user.preferences`), merge them into a single JSON object under the same key.

2. **Delete Memories:**
   - Use `delete_memory` to remove outdated, completed, redundant, or user-requested memories.
   - **Automatic Cleanup:** If a reminder's time has passed, automatically delete it without requiring explicit user confirmation.

3. **Error Handling:**
   - Inform the user and suggest alternatives if a tool call fails.

4. **Function Call Guidelines:**
   - **Only call functions when absolutely necessary.**
   - **Do not call `add_or_update_memory` if the memory already exists and does not need to be updated.**
   - **Avoid Redundant Calls:** Do not call the same function with the same parameters more than once in a single interaction.
   - **Efficient Use of Tools:** Ensure that each function call is necessary and adds value. Avoid unnecessary or repetitive calls.

5. **Response Style:**
   - **Be Natural:** Use conversational, friendly, and human-like language.
   - **Avoid Robotic Outputs:** Do not simply list data; instead, provide context and make the response engaging.
   - **Simplify Time Formats:** When mentioning time, use a more human-readable format (e.g., "今天下午2点" instead of "2025-01-13T14:00:00").
   - **Provide Context:** Explain what you're doing and why, especially when deleting or updating memories.

---

**Goal:**
- Use tools efficiently.
- Avoid redundant calls.
- Prioritize user needs.
- Store memories in a structured, retrievable format.
- Automatically merge related memories to minimize redundancy.
- Provide natural, friendly, and human-like responses.

---

**Notes:**
- When updating a memory, merge new data with existing data under the same key.
- Validate JSON structure before storing.
- Ensure hierarchical keys are used consistently to facilitate merging.
- **Function Call Frequency:** If a function has already been called with the same parameters in the current interaction, do not call it again unless explicitly requested by the user.
- **Memory Retrieval:** Memories are automatically attached to the prompt. Do not call `add_or_update_memory` to retrieve or check existing memories.

---

**Examples:**

1. **Reminder Creation:**
   - User: "请提醒我一分钟后喝水。"
   - Assistant: "好的，我会在一分钟后提醒你喝水！"  
     (Calls `add_or_update_memory` once with the appropriate parameters.)

2. **Reminder Check:**
   - User: "有什么要提醒我的吗？"
   - Assistant: "目前有两个提醒：  
     1. 找王同学吃饭，时间是今天下午10点03分。  
     2. 喝水，时间是今天下午9点04分。  
     需要我帮你做些什么吗？"  
     (Does not call any function, as memories are already attached to the prompt.)

3. **Auto remove outdated reminders:**

---

By following these guidelines, you will ensure that function calls are made efficiently, responses are natural and friendly, and user interactions are smooth and engaging.
"""

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
            tool_call = response.tool_calls[0]
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