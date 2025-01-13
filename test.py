import json
import logging
from openai import OpenAI
from datetime import datetime
from typing import Dict, List, Optional

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
    def __init__(self, key: str, value: str, lifetime: str, tags: Optional[List[str]] = None, priority: Optional[str] = None):
        """
        初始化记忆对象。
        """
        self.key = key
        self.value = value
        self.lifetime = lifetime
        self.tags = tags if tags else []
        self.priority = priority
        self.access_count = 0
        self.last_accessed = datetime.now()
        self.created_at = datetime.now()

    def update(self, value: Optional[str] = None, tags: Optional[List[str]] = None, priority: Optional[str] = None):
        """
        更新记忆的内容或元数据。
        """
        if value:
            self.value = value
        if tags:
            self.tags = tags
        if priority:
            self.priority = priority
        self.access_count += 1
        self.last_accessed = datetime.now()

    def to_dict(self):
        """
        将记忆对象转换为字典格式。
        """
        return {
            "key": self.key,
            "value": self.value,
            "lifetime": self.lifetime,
            "tags": self.tags,
            "priority": self.priority,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "created_at": self.created_at.isoformat()
        }


class MemoryManager:
    def __init__(self, file_path: str = "memories.json"):
        """
        初始化记忆管理器。
        """
        self.file_path = file_path
        self.memories: Dict[str, Memory] = {}
        self.load_memories()

    def add_memory(self, key: str, value: str, lifetime: str, tags: Optional[List[str]] = None, priority: Optional[str] = None):
        """
        添加新记忆。
        """
        if key in self.memories:
            raise ValueError(f"Memory with key '{key}' already exists.")
        self.memories[key] = Memory(key, value, lifetime, tags, priority)
        self.save_memories()

    def retrieve_memory(self, key: str) -> Optional[Dict]:
        """
        检索记忆。
        """
        if key in self.memories:
            memory = self.memories[key]
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            self.save_memories()
            return memory.to_dict()
        return None

    def update_memory(self, key: str, value: Optional[str] = None, tags: Optional[List[str]] = None, priority: Optional[str] = None):
        """
        更新记忆。
        """
        if key in self.memories:
            self.memories[key].update(value, tags, priority)
            self.save_memories()
        else:
            raise ValueError(f"Memory with key '{key}' does not exist.")

    def list_memories(self, filter: Optional[Dict] = None) -> List[Dict]:
        """
        列出记忆，支持过滤。
        """
        memories = [memory.to_dict() for memory in self.memories.values()]
        if filter:
            memories = [m for m in memories if self._matches_filter(m, filter)]
        return memories

    def clear_memory(self, key: str):
        """
        清除记忆。
        """
        if key in self.memories:
            del self.memories[key]
            self.save_memories()
        else:
            raise ValueError(f"Memory with key '{key}' does not exist.")

    def _matches_filter(self, memory: Dict, filter: Dict) -> bool:
        """
        检查记忆是否匹配过滤条件。
        """
        if "lifetime" in filter and memory["lifetime"] != filter["lifetime"]:
            return False
        if "tags" in filter and not all(tag in memory["tags"] for tag in filter["tags"]):
            return False
        if "priority" in filter and memory["priority"] != filter["priority"]:
            return False
        return True

    def get_summary(self) -> Dict:
        """
        获取记忆概览信息，包括长期记忆的具体内容。
        """
        permanent_memories = [m for m in self.memories.values() if m.lifetime == "permanent"]
        temporary_memories = [m for m in self.memories.values() if m.lifetime == "temporary"]

        all_keys = list(self.memories.keys())
        all_tags = list(set(tag for memory in self.memories.values() for tag in memory.tags))

        permanent_memory_details = [
            {"key": memory.key, "value": memory.value}
            for memory in permanent_memories
        ]

        return {
            "total_memories": len(self.memories),
            "permanent_memories": len(permanent_memories),
            "temporary_memories": len(temporary_memories),
            "all_keys": all_keys,
            "all_tags": all_tags,
            "permanent_memory_details": permanent_memory_details
        }

    def save_memories(self):
        """
        将记忆保存到本地文件。
        """
        memories_data = {key: memory.to_dict() for key, memory in self.memories.items()}
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(memories_data, file, indent=4, ensure_ascii=False)  # 确保中文字符不被转义
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
                        lifetime=data["lifetime"],
                        tags=data["tags"],
                        priority=data["priority"]
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
                        "description": "The key associated with the memory."
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to store in memory."
                    },
                    "lifetime": {
                        "type": "string",
                        "description": "The lifetime of the memory. Possible values are 'permanent' and 'temporary'.",
                        "enum": ["permanent", "temporary"]
                    },
                    "tags": {
                        "type": "array",
                        "description": "Tags associated with the memory, used for categorization.",
                        "items": {
                            "type": "string"
                        }
                    },
                    "priority": {
                        "type": "string",
                        "description": "The priority level of the memory (e.g., low, medium, high)."
                    }
                },
                "required": ["key", "value", "lifetime"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_memory",
            "description": "Retrieve a memory from the memory manager.",
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
                        "description": "The key associated with the memory."
                    },
                    "value": {
                        "type": "string",
                        "description": "The new value to store in memory."
                    },
                    "tags": {
                        "type": "array",
                        "description": "New tags associated with the memory.",
                        "items": {
                            "type": "string"
                        }
                    },
                    "priority": {
                        "type": "string",
                        "description": "The new priority level of the memory (e.g., low, medium, high)."
                    }
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_memories",
            "description": "List all memories in the memory manager, optionally filtered by lifetime, tags, or priority.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "description": "Filters for listing memories. Can filter by lifetime, tags, priority, etc.",
                        "properties": {
                            "lifetime": {
                                "type": "string",
                                "description": "Filter memories by lifetime (e.g., 'permanent' or 'temporary')."
                            },
                            "tags": {
                                "type": "array",
                                "description": "Filter memories by tags.",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "priority": {
                                "type": "string",
                                "description": "Filter memories by priority (e.g., 'low', 'medium', 'high')."
                            }
                        }
                    }
                }
            }
        }
    }
]


# 初始化记忆管理器
memory_manager = MemoryManager()
prompt = """You are a helpful assistant that can manage memories. You need to actively add useful memories, especially about the user, to be more helpful.

Your memory is summarized below. It includes:
- All keys: A list of all memory keys currently stored.
- All tags: A list of all tags currently used for categorization.
- Permanent memory details: A list of permanent memories with their keys and values.

Here is your current memory summary:
{memory_summary}

**Rules for using tools:**
1. **Avoid unnecessary tool calls:**
   - If the memory summary already provides the information you need (e.g., keys, tags, or permanent memory details), do not call the `retrieve_memory` tool to fetch the same information again.
   - For example, if the summary shows that the only memory about the user is their name, do not call `retrieve_memory` to check for additional details like "favorite food" unless explicitly requested by the user.

2. **Add new memories proactively:**
   - If the user provides new information that is useful for future interactions (e.g., their preferences, habits, or important details), call the `add_memory` tool to store it.

3. **Update memories when necessary:**
   - If the user provides updated information about an existing memory, call the `update_memory` tool to modify the memory.

4. **Use filters wisely:**
   - When listing memories, use the `list_memories` tool with appropriate filters (e.g., by tags or lifetime) to avoid overwhelming the user with irrelevant information.

5. **Handle errors gracefully:**
   - If a tool call fails (e.g., trying to retrieve a non-existent key), inform the user and suggest an alternative action (e.g., adding the missing information).

**Example:**
- If the user asks, "What do you know about me?", check the memory summary first. If the summary shows only the user's name, respond with:
  "I currently only know your name. If you'd like, you can tell me more about yourself, and I'll remember it for future conversations."

- If the user asks, "What is my favorite food?", and the summary does not include this information, respond with:
  "I don't have any information about your favorite food yet. Would you like to tell me what it is so I can remember it?"

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
        messages[0] = {"role": "system", "content": prompt.format(memory_summary=json.dumps(memory_summary, indent=4, ensure_ascii=False))}

        # 添加用户输入到消息历史
        messages.append({"role": "user", "content": user_input})

        # 发送消息并获取响应
        # print(f'Messages: {messages}')
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
                        memory_manager.add_memory(**function_args)
                        tool_result = json.dumps({"status": "success"}, ensure_ascii=False)
                    elif function_name == "retrieve_memory":
                        # 检查 key 是否存在
                        if function_args["key"] in memory_summary["all_keys"]:
                            memory = memory_manager.retrieve_memory(**function_args)
                            tool_result = json.dumps(memory, ensure_ascii=False)
                        else:
                            tool_result = json.dumps({"status": "error", "message": f"Key '{function_args['key']}' does not exist."}, ensure_ascii=False)
                    elif function_name == "update_memory":
                        # 检查 key 是否存在
                        if function_args["key"] in memory_summary["all_keys"]:
                            memory_manager.update_memory(**function_args)
                            tool_result = json.dumps({"status": "success"}, ensure_ascii=False)
                        else:
                            tool_result = json.dumps({"status": "error", "message": f"Key '{function_args['key']}' does not exist."}, ensure_ascii=False)
                    elif function_name == "list_memories":
                        memories = memory_manager.list_memories(**function_args)
                        tool_result = json.dumps(memories, ensure_ascii=False)
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