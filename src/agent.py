import json
import logging
from openai import OpenAI
from datetime import datetime
from typing import Dict, Optional, List, Set, Union

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
    def __init__(self, key: str, value: Set[Union[str, dict, list, tuple]], created_at: Optional[str] = None, modified_at: Optional[str] = None):
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
            "value": list(self.value),
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

    def save_memory(self, key: str, value: List[Union[str, dict, list, tuple]], override: bool = False):
        """
        保存记忆。如果 override 为 True，则覆盖原有值；否则将新值追加到列表中。
        """
        if not isinstance(value, list):
            value = [value]  # 确保 value 是列表
        value = set(value)  # 使用集合去重
        if key in self.memories and not override:
            # 如果 key 已存在且不覆盖，则将新值追加到列表中
            self.memories[key].value.update(value)
            self.memories[key].modified_at = datetime.now().isoformat()
            status_message = f"successfully updated memory with key '{key}' by appending new value(s)."
        else:
            # 如果 key 不存在或需要覆盖，则创建或覆盖记忆
            self.memories[key] = Memory(key, value)
            status_message = f"successfully added memory with key '{key}' and value '{value}'."
        self.save_memories()
        return {"status": status_message}

    def delete_memory(self, key: str):
        """
        删除记忆。
        """
        if key in self.memories:
            del self.memories[key]
            self.save_memories()
            return {"status": f"successfully deleted memory with key '{key}'."}
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
            "name": "save_memory",
            "description": "Save a memory to the memory manager. If the key already exists, the new value will be appended to the list unless override is set to True.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key associated with the memory (always in English)."
                    },
                    "value": {
                        "type": "array",
                        "items": {
                            "type": ["string", "object", "array"]
                        },
                        "description": "The value(s) to store in memory. Must be a list, even if it contains only one element."
                    },
                    "override": {
                        "type": "boolean",
                        "description": "If True, overwrite the existing value. If False, append the new value to the list.",
                        "default": False
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