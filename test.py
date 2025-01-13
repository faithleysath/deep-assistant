from openai import OpenAI
from datetime import datetime
from typing import Dict, List, Optional

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
    def __init__(self):
        """
        初始化记忆管理器。
        """
        self.memories: Dict[str, Memory] = {}

    def add_memory(self, key: str, value: str, lifetime: str, tags: Optional[List[str]] = None, priority: Optional[str] = None):
        """
        添加新记忆。
        """
        if key in self.memories:
            raise ValueError(f"Memory with key '{key}' already exists.")
        self.memories[key] = Memory(key, value, lifetime, tags, priority)

    def retrieve_memory(self, key: str) -> Optional[Dict]:
        """
        检索记忆。
        """
        if key in self.memories:
            memory = self.memories[key]
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            return memory.to_dict()
        return None

    def update_memory(self, key: str, value: Optional[str] = None, tags: Optional[List[str]] = None, priority: Optional[str] = None):
        """
        更新记忆。
        """
        if key in self.memories:
            self.memories[key].update(value, tags, priority)
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


# 初始化记忆管理器
memory_manager = MemoryManager()

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


# 示例对话
messages = [
    {"role": "system", "content": "You are a helpful assistant that can manage memories."},
    {"role": "user", "content": "Remember that my favorite color is blue."}
]

# 发送消息并获取响应
response = send_messages(messages, tools=tools)

# 处理 LLM 的工具调用
if response.tool_calls:
    for tool_call in response.tool_calls:
        function_name = tool_call.function.name
        function_args = eval(tool_call.function.arguments)

        if function_name == "add_memory":
            memory_manager.add_memory(**function_args)
            print(f"Added memory: {function_args}")

# 打印当前记忆
print("Current memories:", memory_manager.list_memories())