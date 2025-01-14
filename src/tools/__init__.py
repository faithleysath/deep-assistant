import importlib
import pkgutil
import logging
from typing import Dict, List, Any

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.load_tools()

    def load_tools(self):
        """动态加载所有工具"""
        try:
            # 加载builtin目录下的所有工具
            builtin_module = importlib.import_module('src.tools.builtin')
            for _, module_name, _ in pkgutil.iter_modules(builtin_module.__path__):
                module = importlib.import_module(f'src.tools.builtin.{module_name}')
                if hasattr(module, 'tools'):
                    self.tools.update({tool['function']['name']: tool for tool in module.tools})
                    logging.info(f"Loaded tools from {module_name}")
        except Exception as e:
            logging.error(f"Error loading tools: {str(e)}")

    def get_tools(self) -> List[Dict]:
        """获取所有工具"""
        return list(self.tools.values())

    def get_tool(self, tool_name: str) -> Dict:
        """根据名称获取单个工具"""
        return self.tools.get(tool_name)

# 创建全局工具管理器实例
tool_manager = ToolManager()
