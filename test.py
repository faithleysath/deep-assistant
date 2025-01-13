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

    def add_memory(self, key: str, value: str):
        """
        添加记忆。
        """
        if key in self.memories:
            return {"status": "error", "message": f"Memory with key '{key}' already exists."}
        self.memories[key] = Memory(key, value)
        self.save_memories()
        return {"status": "success"}

    def update_memory(self, key: str, value: str):
        """
        更新记忆。
        """
        if key not in self.memories:
            return {"status": "error", "message": f"Memory with key '{key}' does not exist."}
        self.memories[key].value = value
        self.memories[key].modified_at = datetime.now().isoformat()
        self.save_memories()
        return {"status": "success"}

    def delete_memory(self, key: str):
        """
        删除记忆。
        """
        if key in self.memories:
            del self.memories[key]
            self.save_memories()
            return {"status": "success"}
        else:
            return {"status": "error", "message": f"Memory with key '{key}' does not exist."}

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
            "name": "add_memory",
            "description": "Add a new memory to the memory manager.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key associated with the memory (always in English)."
                    },
                    "value": {
                        "type": "string",
                        "description": "The value(s) to store in memory. (better in English, list, set, or dict)"
                    }
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_memory",
            "description": "Update an existing memory in the memory manager.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key associated with the memory (always in English)."
                    },
                    "value": {
                        "type": "string",
                        "description": "The new value to store in memory. (better in English, list, set, or dict)"
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
prompt = """
You are a helpful assistant that manages user memories. Actively add or update useful user-related information for future interactions, ensuring memories are stored in a structured, organized, and retrievable format. Your responses should be natural, friendly, and human-like.

**Current Time:** {current_time}  
**Memory Summary:** {memory_summary}  

---

**Rules:**  
1. **Language for Keys:**  
   - Always use **English** for memory keys (e.g., `user.preferences`, `user.job`).  
   - If the user provides information in another language, translate it to English for the key.  

2. **Key Naming Conventions:**  
   - Clearly distinguish between different types of information. For example:  
     - **Past Actions (曾经做过的):**  
       - `user.past_actions`: Things the user has done in the past.  
     - **Current Actions (现在正在做的):**  
       - `user.current_actions`: Things the user is currently doing.  
     - **Future Plans (将来要做的):**  
       - `user.future_plans`: Things the user plans to do in the future.  
     - **Preferences (偏好):**  
       - `user.favorite_movies`: Movies the user likes.  
       - `user.favorite_books`: Books the user likes.  
     - **Experiences (经历):**  
       - `user.watched_movies`: Movies the user has watched.  
       - `user.read_books`: Books the user has read.  
   - Use descriptive and specific keys to avoid ambiguity.  

3. **Add/Update Memories:**  
   - Use `add_memory` **only for new information**.  
   - Use `update_memory` **only for updating existing information**.  
   - When calling `update_memory`, **always pass the `value` as a structured data type** (e.g., `list`, `dict`, or `set`).  
   - **Do not call `add_memory` multiple times for the same key.** Instead, use `update_memory` to pass structured data.  

4. **Error Handling:**  
   - If a function call fails (e.g., key conflict), **retry** with an appropriate adjustment (e.g., use `update_memory` instead of `add_memory`, be careful not overwrite the old value unless needed. otherwise, use list).  
   - If the error persists, inform the user and ask for clarification.  

5. **Delete Memories:**  
   - Use `delete_memory` to remove outdated, redundant, or user-requested memories.  
   - Automatically delete expired reminders without user confirmation.  

6. **Function Calls:**  
   - Call functions only when necessary.  
   - Avoid redundant or repetitive calls within the same interaction.  

7. **Response Style:**  
   - Be conversational, friendly, and human-like.  

---

**Goal:**  
- Use tools efficiently.  
- Prioritize user needs.  
- Store memories in a structured, retrievable format.  
- Provide natural, engaging, and user-friendly responses.  

---

**Notes:**  
- Do not call `add_memory` or `update_memory` to retrieve or check existing memories (they are automatically attached to the prompt).  
- Always ensure keys are in English and values are stored in a structured format (e.g., `list`, `dict`, or `set`).  
- Clearly distinguish between similar but different concepts (e.g., `user.past_actions` vs. `user.current_actions` vs. `user.future_plans`).  
- **When calling `update_memory`, always pass the `value` as a structured data type (e.g., `list`, `dict`, or `set`).**  

--- 
Before answering the user's question, check if there is any new information to store. If so, store it first.

For example:
User: "I watched Inception last week, do you like it?"
- Store this as `user.watched_movies: ["Inception"]`.
- after store, you can answer the user's question.

User: "I also watched Interstellar, do you like it?"
- Update this as `user.watched_movies: ["Inception", "Interstellar"]`.
- after store, you can answer the user's question.

User: "My favorite genres are sci-fi and action, do you like it?"
- Store this as `user.favorite_genres: ["sci-fi", "action"]`.
- after store, you can answer the user's question.

User: "I have a cat named Whiskers, do you like it?"
- Store this as `user.pets: "cat": "Whiskers"`.
- after store, you can answer the user's question.

You must force yourself to remember as much user information as possible. This includes their past actions, current actions, future plans, preferences, experiences, etc.  
Each time, call `add_memory` or `update_memory` to store user information, unless there is no more information to store.  
When a key can have multiple values, store them as a structured data type (e.g., `list`, `dict`, or `set`).  
You must force yourself to remember as much user information as possible. This includes their past actions, current actions, future plans, preferences, experiences, etc.  
Each time, call `add_memory` or `update_memory` to store user information, unless there is no more information to store.  
When a key can have multiple values, store them as a list (e.g., `user.watched_movies: ["Inception", "Interstellar"]`).  
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
        
        user_input = "Please remember new information about me if needed. If you remember anything, don't tell me what you just remember, just reply me." + user_input
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
                    if function_name == "add_memory":
                        tool_result = memory_manager.add_memory(**function_args)
                    elif function_name == "update_memory":
                        tool_result = memory_manager.update_memory(**function_args)
                    elif function_name == "delete_memory":
                        tool_result = memory_manager.delete_memory(**function_args)
                    else:
                        tool_result = {"status": "error", "message": f"Unknown function: {function_name}"}
                except Exception as e:
                    tool_result = {"status": "error", "message": str(e)}

                # 将工具调用结果添加到消息历史
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(tool_result, ensure_ascii=False)})

            # 再次调用 LLM 以处理工具结果
            response = send_messages(messages, tools=tools)

        # 添加 LLM 响应到消息历史
        if response.content:
            print(f"Assistant: {response.content}")
        messages.append(response)

# 启动对话
if __name__ == "__main__":
    chat()