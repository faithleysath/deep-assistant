import os
import importlib
import logging
from typing import Dict, List, Any, Callable

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Dict] = {}  # 存储工具元数据
        self.functions: Dict[str, Callable] = {}  # 存储工具函数
        self.load_tools()

    def load_tools(self):
        """加载所有工具插件"""
        try:
            # 加载builtin和self_created目录下的工具
            for plugin_dir in ['builtin', 'self_created']:
        except Exception as e:
            logging.error(f"Error loading tools: {str(e)}")
            return
                plugin_path = os.path.join(os.path.dirname(__file__), plugin_dir)
                if not os.path.exists(plugin_path):
                    continue
                    
                for filename in os.listdir(plugin_path):
                    if filename.endswith('.py') and not filename.startswith('__'):
                        module_name = filename[:-3]
                        try:
                            module = importlib.import_module(f'src.tools.{plugin_dir}.{module_name}')
                            if hasattr(module, 'tools') and hasattr(module, 'export'):
                                # 注册工具元数据
                                for tool in module.tools:
                                    self.tools[tool['function']['name']] = tool
                                # 注册工具函数
                                self.functions.update(module.export)
                                logging.info(f"Loaded plugin: {module_name}")
                            # 特殊处理memory插件
                            if module_name == 'memory':
                                self.tools.update({
                                    "save_memory": {
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
                                    "delete_memory": {
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
                                })
                                self.functions.update({
                                    "save_memory": lambda agent_name, key, value, override=False: 
                                        module.MemoryManager(agent_name).save_memory(key, value, override),
                                    "delete_memory": lambda agent_name, key: 
                                        module.MemoryManager(agent_name).delete_memory(key),
                                    "get_summary": lambda agent_name: 
                                        module.MemoryManager(agent_name).get_summary()
                                })
                                logging.info(f"Loaded memory plugin with additional functions")
        except Exception as e:
            logging.error(f"Error loading tools: {str(e)}")

    def get_tools(self) -> List[Dict]:
        """获取所有工具元数据"""
        return list(self.tools.values())

    def get_tool_function(self, tool_name: str) -> Callable:
        """根据名称获取工具函数"""
