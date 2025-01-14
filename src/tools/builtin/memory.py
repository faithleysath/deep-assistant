import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Union
from pathlib import Path

class Memory:
    def __init__(self, key: str, value: Set[Union[str, dict, list, tuple]], 
                 created_at: Optional[str] = None, modified_at: Optional[str] = None):
        self.key = key
        self.value = value
        self.created_at = created_at or datetime.now().isoformat()
        self.modified_at = modified_at or datetime.now().isoformat()

    def to_dict(self):
        return {
            "key": self.key,
            "value": list(self.value),
            "created_at": self.created_at,
            "modified_at": self.modified_at
        }

class MemoryManager:
    _instances: Dict[str, 'MemoryManager'] = {}

    def __new__(cls, agent_name: str) -> 'MemoryManager':
        if agent_name not in cls._instances:
            instance = super().__new__(cls)
            instance.agent_name = agent_name
            instance.memories_dir = Path("memories")
            instance.memories_dir.mkdir(exist_ok=True)
            instance.file_path = instance.memories_dir / f"{agent_name}.json"
            instance.memories: Dict[str, Memory] = {}
            instance.load_memories()
            cls._instances[agent_name] = instance
        return cls._instances[agent_name]

    def __init__(self, agent_name: str):
        """初始化方法仅用于类型提示"""

    def save_memory(self, key: str, value: List[Union[str, dict, list, tuple]], 
                   override: bool = False) -> Dict:
        if not isinstance(value, list):
            value = [value]
        value = set(value)
        
        if key in self.memories and not override:
            self.memories[key].value.update(value)
            self.memories[key].modified_at = datetime.now().isoformat()
            status = f"Updated memory '{key}' for agent '{self.agent_name}'"
        else:
            self.memories[key] = Memory(key, value)
            status = f"Created new memory '{key}' for agent '{self.agent_name}'"
            
        self.save_memories()
        return {"status": "success", "message": status}

    def delete_memory(self, key: str) -> Dict:
        if key in self.memories:
            del self.memories[key]
            self.save_memories()
            return {"status": "success", "message": f"Deleted memory '{key}' for agent '{self.agent_name}'"}
        return {"status": "error", "message": f"Memory '{key}' not found for agent '{self.agent_name}'"}

    def get_summary(self) -> Dict:
        return {
            "agent_name": self.agent_name,
            "total_memories": len(self.memories),
            "all_memories": [memory.to_dict() for memory in self.memories.values()]
        }

    def save_memories(self):
        memories_data = {key: memory.to_dict() for key, memory in self.memories.items()}
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(memories_data, file, indent=4, ensure_ascii=False)

    def load_memories(self):
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding='utf-8') as file:
                    memories_data = json.load(file)
                    self.memories = {
                        key: Memory(
                            key=data["key"],
                            value=set(data["value"]),
                            created_at=data.get("created_at"),
                            modified_at=data.get("modified_at")
                        )
                        for key, data in memories_data.items()
                    }
        except Exception as e:
            logging.error(f"Error loading memories for agent {self.agent_name}: {str(e)}")

# 插件元数据
plugin_metadata = {
    "name": "Memory Manager",
    "version": "1.1.0",
    "description": "Provides memory management capabilities for multiple agents",
    "author": "Cline",
    "features": [
        "Multi-agent memory isolation",
        "Persistent storage",
        "Memory versioning",
        "Memory summary"
    ],
    "config": {
        "storage_path": "memories",
        "max_memory_size": "10MB",
        "auto_save": True
    }
}

# 插件接口
tools = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Save a memory for the current agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "The name of the agent"
                    },
                    "key": {
                        "type": "string",
                        "description": "The key associated with the memory"
                    },
                    "value": {
                        "type": "array",
                        "items": {
                            "type": ["string", "object", "array"]
                        },
                        "description": "The value(s) to store in memory"
                    },
                    "override": {
                        "type": "boolean",
                        "description": "If True, overwrite existing value",
                        "default": False
                    }
                },
                "required": ["agent_name", "key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_memory",
            "description": "Delete a memory for the current agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "The name of the agent"
                    },
                    "key": {
                        "type": "string",
                        "description": "The key associated with the memory"
                    }
                },
                "required": ["agent_name", "key"]
            }
        }
    }
]

# 导出工具函数
export = {
    "save_memory": lambda agent_name, key, value, override=False: 
        MemoryManager(agent_name).save_memory(key, value, override),
    "delete_memory": lambda agent_name, key: 
        MemoryManager(agent_name).delete_memory(key),
    "get_summary": lambda agent_name: 
        MemoryManager(agent_name).get_summary()
}

# 工具管理器扩展功能
def get_plugin_info():
    """获取插件信息"""
    return plugin_metadata

def list_agents():
    """列出所有已存储记忆的agent"""
    memories_dir = Path("memories")
    return [f.stem for f in memories_dir.glob("*.json")]

def cleanup_old_memories(days: int = 30):
    """清理超过指定天数的记忆"""
    cutoff = datetime.now() - timedelta(days=days)
    memories_dir = Path("memories")
    for file in memories_dir.glob("*.json"):
        if file.stat().st_mtime < cutoff.timestamp():
            file.unlink()
            logging.info(f"Removed old memory file: {file.name}")
