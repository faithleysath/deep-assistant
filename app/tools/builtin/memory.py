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
    ]
}

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
        """Singleton pattern to ensure only one instance per agent"""
        if agent_name not in cls._instances:
            instance = super().__new__(cls)
            instance.agent_name = agent_name
            instance.memories_dir = Path("memories")
            instance.memories_dir.mkdir(exist_ok=True)
            instance.file_path = instance.memories_dir / f"{agent_name}.json"
            instance.memories = {}
            instance.load_memories()
            cls._instances[agent_name] = instance
        return cls._instances[agent_name]

    def save_memory(self, key: str, value: List[Union[str, dict, list, tuple]], 
                   override: bool = False) -> Dict:
        if not key or not isinstance(key, str):
            raise ValueError("Key must be a non-empty string")
        if value is None:
            raise ValueError("Value cannot be None")
            
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

    def get_memory(self, key: str) -> Memory:
        if key not in self.memories:
            raise KeyError(f"Memory '{key}' not found for agent '{self.agent_name}'")
        return self.memories[key]

    def save_memories(self, memories_dict: Optional[Dict[str, List[Union[str, dict, list, tuple]]]] = None):
        if memories_dict:
            for key, value in memories_dict.items():
                self.save_memory(key, value)
        self._save_to_file()

    def delete_memories(self, keys: List[str]) -> Dict:
        deleted_count = 0
        for key in keys:
            if key in self.memories:
                del self.memories[key]
                deleted_count += 1
        if deleted_count > 0:
            self._save_to_file()
        return {"status": "success", "message": f"Deleted {deleted_count} memories"}

    def _save_to_file(self):
        memories_data = {key: memory.to_dict() for key, memory in self.memories.items()}
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(memories_data, file, indent=4, ensure_ascii=False)

    def load_from_file(self):
        self.load_memories()

    def delete_memory(self, key: str) -> Dict:
        if key in self.memories:
            del self.memories[key]
            self.save_memories()
            return {"status": "success", "message": f"Deleted memory '{key}' for agent '{self.agent_name}'"}
        return {"status": "error", "message": f"Memory '{key}' not found for agent '{self.agent_name}'"}

    def get_summary(self) -> str:
        summary = f"Agent: {self.agent_name}\n"
        summary += f"Total Memories: {len(self.memories)}\n"
        summary += "Memories:\n"
        for memory in self.memories.values():
            mem_data = memory.to_dict()
            summary += f"- {mem_data['key']} (created: {mem_data['created_at']}, modified: {mem_data['modified_at']})\n"
            for value in mem_data['value']:
                summary += f"  • {str(value)}\n"
        return summary

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

# 插件接口
tools = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Save a memory for the current agent. Stores key-value pairs persistently, with optional override capability. Key supports hierarchical format (e.g. 'user.favorite.movies'). Example: {'key': 'user.favorite.movies', 'value': ['Inception', 'The Matrix']}. Returns {'status': 'success/error', 'message': 'operation result'}",
            "parameters": {
                "type": "object",
                "properties": {
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
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_memory",
            "description": "Delete a memory for the current agent. Removes the specified key and its associated values from persistent storage. Key supports hierarchical format (e.g. 'user.favorite.movies'). Example: {'key': 'user.favorite.movies'}. Returns {'status': 'success/error', 'message': 'operation result'}. Will return error if key not found",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key associated with the memory, supports hierarchical format (e.g. 'user.preferences.theme')"
                    }
                },
                "required": ["key"]
            }
        }
    }
]

# 导出工具函数
exports = {
    "save_memory": lambda agent_name, key, value, override=False: 
        MemoryManager(agent_name).save_memory(key, value, override),
    "delete_memory": lambda agent_name, key: 
        MemoryManager(agent_name).delete_memory(key)
}
