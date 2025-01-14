import os
import importlib
import logging
from typing import Dict, List, Any, Callable

class ToolManager:
    def __init__(self):
        self.tools = []  # 所有工具接口定义
        self.exports = {}  # 所有工具实现
        self.loaded_modules = {}  # 已加载的模块

    def load_tools(self):
        """加载所有工具插件"""
        try:
            # 加载builtin和self_created目录下的工具
            for plugin_dir in ['builtin', 'self_created']:
                plugin_path = os.path.join(os.path.dirname(__file__), plugin_dir)
                if not os.path.exists(plugin_path):
                    logging.warning(f"工具目录 {plugin_path} 不存在")
                    continue
                    
                for filename in os.listdir(plugin_path):
                    if filename.endswith('.py') and not filename.startswith('__'):
                        module_name = filename[:-3]  # 去掉.py后缀
                        
                        try:
                            # 动态加载模块
                            module_path = f"src.tools.{plugin_dir}.{module_name}"
                            module = importlib.import_module(module_path)
