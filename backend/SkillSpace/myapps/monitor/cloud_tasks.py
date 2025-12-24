"""
云服务器监控后台任务
定期采集云服务器数据并通过 WebSocket 推送给前端
"""

import hashlib
import logging
import threading
import time
from datetime import datetime
from typing import Dict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .cloud_collectors import CloudServerCollector
from .config.config_loader import get_config_loader
from .utils.ssh_client import SSHClientManager

logger = logging.getLogger(__name__)


class CloudMonitorTask:
    """云服务器监控后台任务（类似SystemMonitorTask）"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.channel_layer = get_channel_layer()
        self.config_loader = get_config_loader()
        self.ssh_connections = {}  # 缓存SSH连接 {server_name: SSHClientManager}

    def start(self):
        """启动后台监控线程"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("云服务器监控后台任务已启动")

    def stop(self):
        """停止后台监控线程"""
        self.running = False

        # 关闭所有SSH连接
        for server_name, ssh in self.ssh_connections.items():
            try:
                ssh.close()
                logger.info(f"关闭SSH连接: {server_name}")
            except Exception as e:
                logger.error(f"关闭SSH连接失败 {server_name}: {e}")

        self.ssh_connections.clear()

        if self.thread:
            self.thread.join(timeout=5)

        logger.info("云服务器监控后台任务已停止")

    def _run(self):
        """后台线程运行方法"""
        while self.running:
            try:
                # 获取全局配置
                global_config = self.config_loader.get_global_config()
                interval = global_config.get("collect_interval", 10)

                # 获取启用的服务器列表
                servers = self.config_loader.get_servers(enabled_only=True)

                if not servers:
                    logger.debug("没有启用的云服务器配置")
                    time.sleep(interval)
                    continue

                # 遍历所有服务器进行采集
                for server_config in servers:
                    try:
                        # 采集单个服务器数据
                        data = self._collect_server_data(server_config)

                        # 推送到WebSocket
                        server_name = server_config["name"]
                        async_to_sync(self.channel_layer.group_send)(
                            f"cloud_monitor_{hashlib.md5(server_name.encode()).hexdigest()}",
                            {"type": "cloud_status_update", "data": data},
                        )

                        logger.debug(f"数据采集并推送成功: {server_name}")

                    except Exception as e:
                        server_name = server_config.get("name", "Unknown")
                        logger.error(f"采集失败: {server_name} - {e}")

                # 等待下一次采集
                time.sleep(interval)

            except Exception as e:
                logger.error(f"云监控任务异常: {e}")
                time.sleep(10)

    def _collect_server_data(self, server_config: Dict) -> Dict:
        """
        采集单个服务器数据

        Args:
            server_config: 服务器配置字典

        Returns:
            采集的数据字典
        """
        server_name = server_config["name"]
        connection = server_config["connection"]
        monitoring = server_config.get("monitoring", {})

        logger.debug(f"开始采集: {server_name}")

        # 获取或创建SSH连接
        ssh = self._get_ssh_connection(server_name, connection)

        # 创建数据采集器
        collector = CloudServerCollector(ssh)

        # 采集基础系统数据
        data = collector.collect_all()

        # 添加时间戳和服务器名称
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["server_name"] = server_name

        # 采集服务状态
        services = monitoring.get("services", [])
        if services:
            data["services"] = []
            for service_config in services:
                try:
                    service_data = collector.check_service(service_config)
                    data["services"].append(service_data)
                except Exception as e:
                    logger.error(f"采集服务状态失败 {service_config.get('name')}: {e}")

        # 采集Docker容器
        if monitoring.get("enable_docker", False):
            try:
                data["containers"] = collector.collect_docker_containers()
            except Exception as e:
                logger.error(f"采集Docker容器失败: {e}")
                data["containers"] = []

        return data

    def _get_ssh_connection(
        self, server_name: str, connection: Dict
    ) -> SSHClientManager:
        """
        获取或创建SSH连接（支持连接池）

        Args:
            server_name: 服务器名称
            connection: 连接配置

        Returns:
            SSH客户端管理器实例
        """
        # 检查是否已有连接
        if server_name in self.ssh_connections:
            ssh = self.ssh_connections[server_name]
            # 检查连接是否仍然有效
            if ssh.is_alive():
                return ssh
            else:
                # 连接失效，尝试重连
                logger.warning(f"SSH连接失效，尝试重连: {server_name}")
                try:
                    if ssh.reconnect():
                        return ssh
                except Exception as e:
                    pass
                # 重连失败，移除旧连接
                del self.ssh_connections[server_name]

        # 创建新连接
        logger.info(f"创建新的SSH连接: {server_name}")

        ssh = SSHClientManager(
            host=connection["host"],
            port=connection["port"],
            username=connection["username"],
            password=connection.get("password"),
            key_path=connection.get("private_key_path"),
            passphrase=connection.get("passphrase"),
            timeout=connection.get("timeout", 10),
        )

        # 建立连接
        ssh.connect()

        # 缓存连接
        self.ssh_connections[server_name] = ssh

        return ssh

    def reload_config(self):
        """
        重新加载配置（用于配置文件变更后更新）
        """
        try:
            logger.info("重新加载云服务器配置")
            self.config_loader.reload()

            # 关闭不再存在或被禁用的服务器连接
            current_servers = {
                s["name"] for s in self.config_loader.get_servers(enabled_only=True)
            }
            to_remove = []

            for server_name in self.ssh_connections.keys():
                if server_name not in current_servers:
                    to_remove.append(server_name)

            for server_name in to_remove:
                ssh = self.ssh_connections[server_name]
                ssh.close()
                del self.ssh_connections[server_name]
                logger.info(f"移除SSH连接: {server_name}")

        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")


# 全局单例
_cloud_monitor_task = None


def get_cloud_monitor_task() -> CloudMonitorTask:
    """
    获取云监控任务单例

    Returns:
        CloudMonitorTask实例
    """
    global _cloud_monitor_task
    if _cloud_monitor_task is None:
        _cloud_monitor_task = CloudMonitorTask()
    return _cloud_monitor_task


def reset_cloud_monitor_task():
    """
    重置云监控任务单例（主要用于测试）
    """
    global _cloud_monitor_task
    if _cloud_monitor_task:
        _cloud_monitor_task.stop()
    _cloud_monitor_task = None
