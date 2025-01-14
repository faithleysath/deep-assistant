import yaml
from pathlib import Path

class Config:
    """配置类"""
    def __init__(self, config_file="config.yaml"):
        self.config_file = Path(config_file)
        self._config = None
        self._load_config()

    def _load_config(self):
        """加载 YAML 配置文件"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"配置文件 {self.config_file} 不存在！")

    def get(self, section, key=None, default=None):
        """
        获取配置值
        :param section: 配置的一级键，例如 'file_paths'
        :param key: 配置的二级键，例如 'data_file'，可选
        :param default: 如果未找到对应键，返回的默认值
        :return: 配置值或默认值
        """
        if key is None:
            return self._config.get(section, default)
        return self._config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """
        设置配置值
        :param section: 配置的一级键，例如 'file_paths'
        :param key: 配置的二级键，例如 'data_file'
        :param value: 要设置的值
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value

    def save(self):
        """将配置保存回 YAML 文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

    def reload(self):
        """重新加载配置文件"""
        self._load_config()

# 创建 Config 实例（单例）
config = Config(config_file="config1.yaml")
