"""
Linux本地系统监控数据采集器
使用psutil直接读取本地Linux系统信息（无需SSH）
适用于部署在Linux云服务器上的自我监控
"""

import logging
import platform
import socket
from datetime import datetime
from typing import Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class LocalLinuxCollector:
    """
    Linux本地系统数据采集器
    使用psutil直接读取本地系统信息，无需SSH连接
    """

    def __init__(self):
        """初始化采集器"""
        self.hostname = socket.gethostname()
        logger.info(f"初始化本地Linux监控: {self.hostname}")

    def collect_all(self) -> Dict:
        """
        采集所有系统数据

        Returns:
            包含所有监控数据的字典
        """
        try:
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "system": self.collect_system_info(),
                "cpu": self.collect_cpu_info(),
                "memory": self.collect_memory_info(),
                "disk": self.collect_disk_info(),
                "network": self.collect_network_info(),
                "services": [],  # 可选：如果需要监控服务
                "containers": [],  # 可选：如果需要监控Docker
            }
        except Exception as e:
            logger.error(f"数据采集失败: {e}")
            raise

    def collect_system_info(self) -> Dict:
        """
        采集系统基本信息

        Returns:
            系统信息字典
        """
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_seconds = (datetime.now() - boot_time).total_seconds()

            # 计算运行时间
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)

            if days > 0:
                uptime_str = f"{days}天 {hours}小时 {minutes}分钟"
            elif hours > 0:
                uptime_str = f"{hours}小时 {minutes}分钟"
            else:
                uptime_str = f"{minutes}分钟"

            return {
                "hostname": self.hostname,
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor() or "Unknown",
                "uptime": uptime_str,
                "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            logger.error(f"采集系统信息失败: {e}")
            return {"hostname": self.hostname, "uptime": "Unknown"}

    def collect_cpu_info(self) -> Dict:
        """
        采集CPU信息

        Returns:
            CPU信息字典
        """
        try:
            # CPU使用率（等待1秒获取准确值）
            cpu_percent = psutil.cpu_percent(interval=1)

            # CPU核心数
            physical_cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)

            # 负载平均值（仅Linux）
            if hasattr(psutil, "getloadavg"):
                load_avg = psutil.getloadavg()
                load_avg_1 = round(load_avg[0], 2)
                load_avg_5 = round(load_avg[1], 2)
                load_avg_15 = round(load_avg[2], 2)
            else:
                load_avg_1 = load_avg_5 = load_avg_15 = 0.0

            # CPU频率
            cpu_freq = psutil.cpu_freq()
            current_freq = round(cpu_freq.current, 2) if cpu_freq else 0

            return {
                "usage_percent": round(cpu_percent, 2),
                "cores": logical_cores or physical_cores,
                "physical_cores": physical_cores,
                "logical_cores": logical_cores,
                "current_freq": current_freq,
                "load_avg_1": load_avg_1,
                "load_avg_5": load_avg_5,
                "load_avg_15": load_avg_15,
                "per_core_usage": [
                    round(x, 2) for x in psutil.cpu_percent(percpu=True)
                ],
            }
        except Exception as e:
            logger.error(f"采集CPU信息失败: {e}")
            return {
                "usage_percent": 0,
                "cores": 0,
                "load_avg_1": 0,
                "load_avg_5": 0,
                "load_avg_15": 0,
            }

    def collect_memory_info(self) -> Dict:
        """
        采集内存信息

        Returns:
            内存信息字典
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "free": mem.free,
                "usage_percent": round(mem.percent, 2),
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_free": swap.free,
                "swap_percent": round(swap.percent, 2),
            }
        except Exception as e:
            logger.error(f"采集内存信息失败: {e}")
            return {"total": 0, "used": 0, "available": 0, "usage_percent": 0}

    def collect_disk_info(self) -> Dict:
        """
        采集磁盘信息

        Returns:
            磁盘信息字典
        """
        try:
            # 获取所有磁盘分区
            partitions = psutil.disk_partitions()

            total_size = 0
            total_used = 0
            total_free = 0
            partition_list = []

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)

                    # 跳过特殊文件系统
                    if partition.fstype in ["tmpfs", "devtmpfs", "squashfs"]:
                        continue

                    total_size += usage.total
                    total_used += usage.used
                    total_free += usage.free

                    partition_list.append(
                        {
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": round(usage.percent, 2),
                        }
                    )
                except PermissionError:
                    continue

            usage_percent = (
                round((total_used / total_size * 100), 2) if total_size > 0 else 0
            )

            return {
                "total": total_size,
                "used": total_used,
                "free": total_free,
                "usage_percent": usage_percent,
                "partitions": partition_list,
            }
        except Exception as e:
            logger.error(f"采集磁盘信息失败: {e}")
            return {
                "total": 0,
                "used": 0,
                "free": 0,
                "usage_percent": 0,
                "partitions": [],
            }

    def collect_network_info(self) -> Dict:
        """
        采集网络信息

        Returns:
            网络信息字典
        """
        try:
            net_io = psutil.net_io_counters()

            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
            }
        except Exception as e:
            logger.error(f"采集网络信息失败: {e}")
            return {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0,
            }

    def check_service(self, service_name: str) -> Dict:
        """
        检查服务状态（可选功能）

        Args:
            service_name: 服务名称

        Returns:
            服务状态字典
        """
        try:
            # 遍历所有进程查找服务
            for proc in psutil.process_iter(["name", "status"]):
                if service_name.lower() in proc.info["name"].lower():
                    return {"name": service_name, "status": "running", "pid": proc.pid}

            return {"name": service_name, "status": "stopped", "pid": None}
        except Exception as e:
            logger.error(f"检查服务状态失败: {service_name} - {e}")
            return {"name": service_name, "status": "unknown", "pid": None}


# 单例模式
_local_collector_instance = None


def get_local_collector() -> LocalLinuxCollector:
    """
    获取本地采集器单例

    Returns:
        LocalLinuxCollector实例
    """
    global _local_collector_instance
    if _local_collector_instance is None:
        _local_collector_instance = LocalLinuxCollector()
    return _local_collector_instance
