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
                        

# 创建全局工具管理器实例
tool_manager = ToolManager()
