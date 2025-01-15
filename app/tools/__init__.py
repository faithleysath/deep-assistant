import os
import importlib
import pkgutil
import logging

class ToolManager:
    def __init__(self):
        self.tools = []  # 所有工具接口定义
        self.exports = {}  # 所有工具实现
        self.loaded_modules = {}  # 已加载的模块

    def load_tools(self):
        """加载所有工具插件
        """
        try:
            self.tools.clear()
            self.exports.clear()
            self.loaded_modules.clear()
                
            # 加载builtin和self_created目录下的工具
            for plugin_dir in ['builtin', 'self_created']:
                plugin_path = os.path.join(os.path.dirname(__file__), plugin_dir)
                if not os.path.exists(plugin_path):
                    logging.warning(f"工具目录 {plugin_path} 不存在")
                    continue
                    
                # 使用pkgutil遍历模块
                for finder, name, ispkg in pkgutil.iter_modules([plugin_path]):
                    if not ispkg and not name.startswith('__'):
                        try:
                            # 动态加载模块
                            # 重新加载模块
                            if name in self.loaded_modules:
                                module = importlib.reload(self.loaded_modules[name])
                            else:
                                module = importlib.import_module(f'app.tools.{plugin_dir}.{name}')
                            self.loaded_modules[name] = module
                            
                            # 检查metadata中的enable字段
                            if hasattr(module, 'metadata') and hasattr(module.metadata, 'enable'):
                                if not module.metadata.enable:
                                    logging.info(f"跳过未启用的工具模块: {name}")
                                    continue
                            
                            # 收集工具接口
                            if hasattr(module, 'tools'):
                                self.tools.extend(module.tools)
                                
                            # 收集工具实现
                            if hasattr(module, 'exports'):
                                for func_name, func in module.exports.items():
                                    if func_name in self.exports:
                                        raise ValueError(f"工具函数 {func_name} 已存在，请检查工具定义")
                                    self.exports[func_name] = func
                                    
                        except ImportError as e:
                            logging.error(f"无法导入工具模块 {name}: {str(e)}")
                        except Exception as e:
                            logging.error(f"加载工具模块 {name} 时发生错误: {str(e)}")
                            
            logging.info(f"成功加载 {len(self.tools)} 个工具接口和 {len(self.exports)} 个工具实现")
            return True
            
        except Exception as e:
            logging.error(f"加载工具时发生严重错误: {str(e)}")
            return False
        finally:
            logging.debug("工具加载过程完成")

# 创建全局工具管理器实例并导出
tool_manager = ToolManager()
tool_manager.load_tools()

__all__ = ['ToolManager', 'tool_manager']
