"""
执行机客户端配置管理
- 存储配置到本地 JSON 文件
- 提供6个配置项的读写接口
- 生成和存储 UUID
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ExecutorConfig:
    """执行机配置数据类"""
    # 服务器配置
    server_url: str = "http://127.0.0.1:8000"  # 改为 HTTP
    server_token: str = ""  # 登录后获取的token

    # 执行机身份
    executor_uuid: str = ""  # 自动生成UUID
    executor_name: str = ""
    owner_username: str = ""  # 所有者用户名
    owner_password: str = ""  # 所有者密码

    # 执行配置
    max_concurrent: int = 3  # 最大并发任务数

    # 浏览器配置
    default_browser: str = "chrome"  # 默认浏览器: chrome/firefox/edge
    chrome_path: str = ""  # Chrome浏览器路径
    chrome_driver_path: str = ""  # ChromeDriver路径
    firefox_path: str = ""  # Firefox浏览器路径
    firefox_driver_path: str = ""  # GeckoDriver路径
    edge_path: str = ""  # Edge浏览器路径
    edge_driver_path: str = ""  # EdgeDriver路径

    # 日志配置
    log_retention_days: int = 7
    log_level: str = "WARNING"  # 降低日志级别以减少输出
    log_max_size_mb: int = 50

    # 心跳配置
    heartbeat_interval: int = 30  # 秒
    heartbeat_fail_threshold: int = 5  # 连续失败次数阈值

    # RabbitMQ 配置
    rabbitmq_host: str = "127.0.0.1"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"

    # 其他
    is_enabled: bool = True
    description: str = ""


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，默认为 ~/.executor/config.json
        """
        if config_path is None:
            # 默认配置路径
            home_dir = Path.home()
            config_dir = home_dir / ".executor"
            config_dir.mkdir(exist_ok=True)
            config_path = str(config_dir / "config.json")

        self.config_path = config_path
        self.config = self._load()

    def _load(self) -> ExecutorConfig:
        """从文件加载配置"""
        config_file = Path(self.config_path)

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ExecutorConfig(**data)
            except Exception as e:
                print(f"加载配置失败: {e}，使用默认配置")
                return ExecutorConfig()
        else:
            # 首次运行，生成UUID并保存
            config = ExecutorConfig()
            config.executor_uuid = str(uuid.uuid4())
            self.save(config)
            return config

    def save(self, config: ExecutorConfig = None) -> bool:
        """
        保存配置到文件

        Args:
            config: 要保存的配置，为None时保存当前配置

        Returns:
            是否保存成功
        """
        if config is not None:
            self.config = config

        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(exist_ok=True)

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get(self) -> ExecutorConfig:
        """获取当前配置"""
        return self.config

    def update(self, **kwargs) -> bool:
        """
        更新配置项

        Args:
            **kwargs: 要更新的配置键值对

        Returns:
            是否更新成功
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        return self.save()

    def is_configured(self) -> bool:
        """
        检查是否已完成基本配置

        Returns:
            是否已完成基本配置（至少配置了服务器地址和用户名密码）
        """
        return bool(
            self.config.server_url and
            self.config.owner_username and
            self.config.owner_password
        )

    def get_auth_headers(self) -> Dict[str, str]:
        """
        获取认证头

        Returns:
            包含token的请求头
        """
        return {
            "Authorization": f"Token {self.config.server_token}",
            "X-Executor-UUID": self.config.executor_uuid
        }


# 单例模式
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取配置管理器单例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
