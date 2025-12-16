# monitor/tasks.py
"""
系统监控后台任务
每秒采集一次系统数据并通过 WebSocket 推送给前端
"""
import asyncio
import json
import logging
import platform
import threading
import time
from datetime import datetime

import psutil
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import connection

logger = logging.getLogger(__name__)


class SystemMonitorTask:
    """系统监控后台任务"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.channel_layer = get_channel_layer()

    def start(self):
        """启动后台监控线程"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("系统监控后台任务已启动")

    def stop(self):
        """停止后台监控线程"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("系统监控后台任务已停止")

    def _run(self):
        """后台线程运行方法"""
        while self.running:
            try:
                # 采集系统数据
                system_data = self._collect_system_data()

                # 通过 Channel Layer 发送数据到 WebSocket
                async_to_sync(self.channel_layer.group_send)(
                    'system_monitor',
                    {
                        'type': 'system_status_update',
                        'data': system_data
                    }
                )

                # 等待1秒后继续下一次采集
                time.sleep(1)

            except Exception as e:
                logger.error(f"系统监控任务出错: {e}")
                time.sleep(1)

    def _collect_system_data(self):
        """采集系统数据"""
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'system': self._get_system_info(),
            'cpu': self._get_cpu_info(),
            'memory': self._get_memory_info(),
            'disk': self._get_disk_info(),
            'network': self._get_network_info(),
            'database': self._get_database_info()
        }

    def _get_system_info(self):
        """获取系统基本信息"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60

        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': f'{days}天 {hours}小时 {minutes}分钟',
            'uptime_seconds': int(uptime.total_seconds())
        }

    def _get_cpu_info(self):
        """获取CPU信息"""
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()

        # 获取每个核心的使用率
        cpu_per_core = psutil.cpu_percent(interval=0.5, percpu=True)

        return {
            'usage_percent': round(cpu_percent, 2),
            'physical_cores': cpu_count,
            'logical_cores': cpu_count_logical,
            'current_freq': round(cpu_freq.current, 2) if cpu_freq else 0,
            'max_freq': round(cpu_freq.max, 2) if cpu_freq else 0,
            'min_freq': round(cpu_freq.min, 2) if cpu_freq else 0,
            'per_core_usage': [round(x, 2) for x in cpu_per_core]
        }

    def _get_memory_info(self):
        """获取内存信息"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            'total': self._bytes_to_gb(memory.total),
            'available': self._bytes_to_gb(memory.available),
            'used': self._bytes_to_gb(memory.used),
            'free': self._bytes_to_gb(memory.free),
            'usage_percent': round(memory.percent, 2),
            'swap_total': self._bytes_to_gb(swap.total),
            'swap_used': self._bytes_to_gb(swap.used),
            'swap_free': self._bytes_to_gb(swap.free),
            'swap_percent': round(swap.percent, 2)
        }

    def _get_disk_info(self):
        """获取磁盘信息"""
        disk_partitions = psutil.disk_partitions()
        disk_list = []

        for partition in disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_list.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': self._bytes_to_gb(usage.total),
                    'used': self._bytes_to_gb(usage.used),
                    'free': self._bytes_to_gb(usage.free),
                    'usage_percent': round(usage.percent, 2)
                })
            except PermissionError:
                continue

        # 磁盘IO统计
        disk_io = psutil.disk_io_counters()
        io_stats = {
            'read_count': disk_io.read_count,
            'write_count': disk_io.write_count,
            'read_bytes': self._bytes_to_gb(disk_io.read_bytes),
            'write_bytes': self._bytes_to_gb(disk_io.write_bytes)
        } if disk_io else {}

        return {
            'partitions': disk_list,
            'io_stats': io_stats
        }

    def _get_network_info(self):
        """获取网络信息"""
        network_io = psutil.net_io_counters()

        return {
            'bytes_sent': self._bytes_to_gb(network_io.bytes_sent),
            'bytes_recv': self._bytes_to_gb(network_io.bytes_recv),
            'packets_sent': network_io.packets_sent,
            'packets_recv': network_io.packets_recv,
            'errors_in': network_io.errin,
            'errors_out': network_io.errout,
            'drop_in': network_io.dropin,
            'drop_out': network_io.dropout
        }

    def _get_database_info(self):
        """获取数据库连接信息"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0] if cursor.rowcount > 0 else "Unknown"

                cursor.execute("""
                    SELECT pg_database.datname,
                           pg_size_pretty(pg_database_size(pg_database.datname)) AS size
                    FROM pg_database
                    WHERE datname = current_database()
                """)
                db_size_result = cursor.fetchone()
                db_size = db_size_result[1] if db_size_result else "Unknown"

                return {
                    'version': db_version,
                    'database_name': connection.settings_dict['NAME'],
                    'size': db_size,
                    'status': 'connected'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def _bytes_to_gb(self, bytes_value):
        """字节转GB"""
        return round(bytes_value / (1024 ** 3), 2)


# 全局单例
_monitor_task = SystemMonitorTask()


def get_monitor_task():
    """获取监控任务单例"""
    return _monitor_task
