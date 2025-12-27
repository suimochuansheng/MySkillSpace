"""
云服务器配置文件加载器
负责读取和解析 cloud_servers.yaml 配置文件
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class CloudServerConfigLoader:
    """云服务器配置文件加载器"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置加载器

        Args:
            config_file: 配置文件路径，默认为 config/cloud_servers.yaml
        """
        if config_file is None:
            # 默认配置文件路径
            current_dir = Path(__file__).parent
            config_file = current_dir / "cloud_servers.yaml"

        self.config_file = Path(config_file)
        self.config_data = None
        self.last_modified = None

    def load(self, force_reload: bool = False) -> Dict:
        """
        加载配置文件

        Args:
            force_reload: 是否强制重新加载

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        # 如果已经有内存配置且不强制重载，直接返回（支持手动设置的配置）
        if not force_reload and self.config_data is not None:
            logger.debug("使用已加载的配置")
            return self.config_data

        # 检查文件是否存在
        if not self.config_file.exists():
            # 如果有内存配置，即使文件不存在也返回内存配置
            if self.config_data is not None:
                logger.debug("配置文件不存在，但使用内存配置")
                return self.config_data

            raise FileNotFoundError(
                f"配置文件不存在: {self.config_file}\n"
                f"请复制 cloud_servers.example.yaml 为 cloud_servers.yaml 并填写配置"
            )

        # 获取文件修改时间
        current_modified = self.config_file.stat().st_mtime

        # 如果文件未修改且不强制重载，返回缓存的配置
        if not force_reload and self.config_data is not None:
            if self.last_modified == current_modified:
                logger.debug("使用缓存的配置")
                return self.config_data

        # 加载配置文件
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config_data = yaml.safe_load(f)

            self.last_modified = current_modified
            logger.info(f"成功加载配置文件: {self.config_file}")

            # 验证配置
            self._validate_config()

            return self.config_data

        except yaml.YAMLError as e:
            logger.error(f"配置文件解析失败: {e}")
            raise ValueError(f"YAML格式错误: {e}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    def _validate_config(self):
        """
        验证配置文件基本格式

        Raises:
            ValueError: 配置格式错误
        """
        if not self.config_data:
            raise ValueError("配置文件为空")

        if "servers" not in self.config_data:
            raise ValueError("配置文件缺少 'servers' 字段")

        servers = self.config_data.get("servers", [])
        if not isinstance(servers, list):
            raise ValueError("'servers' 必须是列表类型")

        # 验证每个服务器配置
        for i, server in enumerate(servers):
            self._validate_server_config(server, i)

        logger.debug("配置文件验证通过")

    def _validate_server_config(self, server: Dict, index: int):
        """
        验证单个服务器配置

        Args:
            server: 服务器配置字典
            index: 服务器索引

        Raises:
            ValueError: 配置格式错误
        """
        prefix = f"servers[{index}]"

        # 验证必填字段
        required_fields = ["name", "connection"]
        for field in required_fields:
            if field not in server:
                raise ValueError(f"{prefix} 缺少必填字段: {field}")

        # 验证name
        if not isinstance(server["name"], str) or not server["name"].strip():
            raise ValueError(f"{prefix}.name 必须是非空字符串")

        # 验证connection
        connection = server.get("connection", {})
        if not isinstance(connection, dict):
            raise ValueError(f"{prefix}.connection 必须是字典类型")

        # 验证connection必填字段
        conn_required = ["host", "port", "username", "auth_type"]
        for field in conn_required:
            if field not in connection:
                raise ValueError(f"{prefix}.connection 缺少必填字段: {field}")

        # 验证auth_type
        auth_type = connection.get("auth_type")
        if auth_type not in ["password", "key"]:
            raise ValueError(
                f"{prefix}.connection.auth_type 必须是 'password' 或 'key'"
            )

        # 验证认证信息
        if auth_type == "password":
            if "password" not in connection or not connection["password"]:
                raise ValueError(f"{prefix}.connection 使用密码认证时必须提供 password")
        elif auth_type == "key":
            if (
                "private_key_path" not in connection
                or not connection["private_key_path"]
            ):
                raise ValueError(
                    f"{prefix}.connection 使用密钥认证时必须提供 private_key_path"
                )

    def get_global_config(self) -> Dict:
        """
        获取全局配置

        Returns:
            全局配置字典
        """
        config = self.load()
        return config.get("global", {})

    def get_servers(self, enabled_only: bool = True) -> List[Dict]:
        """
        获取服务器列表

        Args:
            enabled_only: 是否仅返回启用的服务器

        Returns:
            服务器配置列表
        """
        config = self.load()
        servers = config.get("servers", [])

        if enabled_only:
            servers = [s for s in servers if s.get("enabled", True)]

        return servers

    def get_server_by_name(self, name: str) -> Optional[Dict]:
        """
        根据名称获取服务器配置

        Args:
            name: 服务器名称

        Returns:
            服务器配置字典，不存在则返回None
        """
        servers = self.get_servers(enabled_only=False)
        for server in servers:
            if server.get("name") == name:
                return server
        return None

    def get_servers_by_tag(self, tag: str) -> List[Dict]:
        """
        根据标签获取服务器列表

        Args:
            tag: 标签名称

        Returns:
            匹配的服务器列表
        """
        servers = self.get_servers(enabled_only=True)
        return [s for s in servers if tag in s.get("tags", [])]

    def reload(self) -> Dict:
        """
        强制重新加载配置文件

        Returns:
            配置字典
        """
        return self.load(force_reload=True)

    def get_server_count(self, enabled_only: bool = True) -> int:
        """
        获取服务器数量

        Args:
            enabled_only: 是否仅统计启用的服务器

        Returns:
            服务器数量
        """
        servers = self.get_servers(enabled_only=enabled_only)
        return len(servers)

    def __repr__(self):
        """字符串表示"""
        if self.config_data:
            server_count = self.get_server_count(enabled_only=False)
            enabled_count = self.get_server_count(enabled_only=True)
            return f"<CloudServerConfigLoader servers={server_count} enabled={enabled_count}>"
        else:
            return "<CloudServerConfigLoader [未加载]>"


# 全局单例
_config_loader_instance = None


def get_config_loader() -> CloudServerConfigLoader:
    """
    获取配置加载器单例

    Returns:
        配置加载器实例
    """
    global _config_loader_instance
    if _config_loader_instance is None:
        _config_loader_instance = CloudServerConfigLoader()
    return _config_loader_instance


def reset_config_loader():
    """
    重置配置加载器单例（主要用于测试）
    """
    global _config_loader_instance
    _config_loader_instance = None
