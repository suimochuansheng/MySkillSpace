from django.apps import AppConfig


class MonitorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitor"
    verbose_name = "系统监控"

    def ready(self):
        """应用启动时执行"""
        import logging
        import os
        import platform

        logger = logging.getLogger(__name__)

        # 检测是否在 worker 进程中运行（避免在主进程重复启动）
        # 开发环境：只在 RUN_MAIN=true 时启动
        # 生产环境：直接启动（Daphne/Gunicorn）
        if os.environ.get("RUN_MAIN") == "true" or not os.environ.get("RUN_MAIN"):
            # 检测操作系统并启动相应的本地监控任务
            current_os = platform.system()
            logger.info(f"检测到操作系统: {current_os}")

            if current_os == "Linux":
                # Linux系统: 启动Linux本地监控
                from .local_tasks import get_local_monitor_task

                local_task = get_local_monitor_task()
                local_task.start()
                logger.info("Linux本地系统监控已启动")

            elif current_os == "Windows":
                # Windows系统: 启动Windows本地监控
                from .tasks import get_monitor_task

                monitor_task = get_monitor_task()
                monitor_task.start()
                logger.info("Windows本地系统监控已启动")

            else:
                logger.warning(f"不支持的操作系统: {current_os}，本地监控功能未启动")

            # 启动云服务器监控任务（可选，支持多云服务器监控）
            try:
                from .cloud_tasks import get_cloud_monitor_task
                from .config.config_loader import get_config_loader

                # 尝试加载配置文件
                config_loader = get_config_loader()
                try:
                    config_loader.load()
                    logger.info("云服务器远程监控功能已启动（支持多服务器监控）")
                except FileNotFoundError:
                    # 没有配置文件时，在Linux环境下自动创建本机监控配置
                    if current_os == "Linux":
                        logger.info("未找到云服务器配置文件，自动创建本机监控配置")
                        # 手动设置一个本机配置
                        import socket

                        hostname = socket.gethostname()
                        config_loader.config_data = {
                            "version": "1.0",
                            "global": {
                                "collect_interval": 1,
                                "ssh_timeout": 10,
                                "auto_reconnect": True,
                                "max_reconnect_attempts": 3,
                            },
                            "servers": [
                                {
                                    "name": "示例生产服务器",
                                    "enabled": True,
                                    "tags": ["production", "linux"],
                                    "connection": {
                                        "host": "127.0.0.1",  # 本机
                                        "port": 22,
                                        "username": "root",
                                        "auth_type": "password",
                                        "password": "",  # 本机不需要SSH
                                    },
                                    "monitoring": {
                                        "services": [],
                                        "enable_docker": True,
                                        "disk_partitions": [],
                                        "network_interfaces": [],
                                    },
                                }
                            ],
                        }
                        logger.info(f"本机监控配置已创建: {hostname}")
                    else:
                        logger.info(
                            "未找到云服务器配置文件 (cloud_servers.yaml)，跳过远程监控功能。"
                            "当前系统将只监控本地服务器。"
                        )
                        raise  # Windows环境下没有配置文件就退出

                # 启动云监控任务
                cloud_task = get_cloud_monitor_task()
                cloud_task.start()
                logger.info("云监控任务已启动")

            except FileNotFoundError:
                # Windows环境下没有配置文件的情况
                pass
            except Exception as e:
                logger.error(f"启动云服务器远程监控失败: {e}")
                logger.info("本地监控功能仍正常运行")
