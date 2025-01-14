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
                        except Exception as e:
                            logging.error(f"Error loading plugin {module_name}: {str(e)}")
        except Exception as e:
            logging.error(f"Error loading tools: {str(e)}")

    def get_tools(self) -> List[Dict]:
        """获取所有工具元数据"""
        return list(self.tools.values())

    def get_tool_function(self, tool_name: str) -> Callable:
        """根据名称获取工具函数"""
        return self.functions.get(tool_name)

# 创建全局工具管理器实例
tool_manager = ToolManager()
