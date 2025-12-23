# monitor/views.py
import platform
from datetime import datetime

import psutil
from django.db import connection
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class SystemStatusView(APIView):
    """
    系统状态监控API
    返回服务器的CPU、内存、磁盘、网络等信息
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 获取系统信息
            system_info = self.get_system_info()

            # 获取CPU信息
            cpu_info = self.get_cpu_info()

            # 获取内存信息
            memory_info = self.get_memory_info()

            # 获取磁盘信息
            disk_info = self.get_disk_info()

            # 获取网络信息
            network_info = self.get_network_info()

            # 获取数据库信息
            database_info = self.get_database_info()

            return Response(
                {
                    "code": 200,
                    "data": {
                        "system": system_info,
                        "cpu": cpu_info,
                        "memory": memory_info,
                        "disk": disk_info,
                        "network": network_info,
                        "database": database_info,
                    },
                }
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": f"获取系统状态失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_system_info(self):
        """获取系统基本信息"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        # 计算运行天数、小时、分钟
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60

        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "processor": platform.processor(),
            "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime": f"{days}天 {hours}小时 {minutes}分钟",
            "uptime_seconds": int(uptime.total_seconds()),
        }

    def get_cpu_info(self):
        """获取CPU信息"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=False)  # 物理核心数
        cpu_count_logical = psutil.cpu_count(logical=True)  # 逻辑核心数
        cpu_freq = psutil.cpu_freq()

        return {
            "usage_percent": round(cpu_percent, 2),
            "physical_cores": cpu_count,
            "logical_cores": cpu_count_logical,
            "current_freq": round(cpu_freq.current, 2) if cpu_freq else 0,
            "max_freq": round(cpu_freq.max, 2) if cpu_freq else 0,
            "min_freq": round(cpu_freq.min, 2) if cpu_freq else 0,
        }

    def get_memory_info(self):
        """获取内存信息"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "total": self._bytes_to_gb(memory.total),
            "available": self._bytes_to_gb(memory.available),
            "used": self._bytes_to_gb(memory.used),
            "free": self._bytes_to_gb(memory.free),
            "usage_percent": round(memory.percent, 2),
            "swap_total": self._bytes_to_gb(swap.total),
            "swap_used": self._bytes_to_gb(swap.used),
            "swap_free": self._bytes_to_gb(swap.free),
            "swap_percent": round(swap.percent, 2),
        }

    def get_disk_info(self):
        """获取磁盘信息"""
        disk_partitions = psutil.disk_partitions()
        disk_list = []

        for partition in disk_partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_list.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": self._bytes_to_gb(usage.total),
                        "used": self._bytes_to_gb(usage.used),
                        "free": self._bytes_to_gb(usage.free),
                        "usage_percent": round(usage.percent, 2),
                    }
                )
            except PermissionError:
                continue

        # 磁盘IO统计
        disk_io = psutil.disk_io_counters()
        io_stats = (
            {
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count,
                "read_bytes": self._bytes_to_gb(disk_io.read_bytes),
                "write_bytes": self._bytes_to_gb(disk_io.write_bytes),
            }
            if disk_io
            else {}
        )

        return {"partitions": disk_list, "io_stats": io_stats}

    def get_network_info(self):
        """获取网络信息"""
        network_io = psutil.net_io_counters()

        return {
            "bytes_sent": self._bytes_to_gb(network_io.bytes_sent),
            "bytes_recv": self._bytes_to_gb(network_io.bytes_recv),
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv,
            "errors_in": network_io.errin,
            "errors_out": network_io.errout,
            "drop_in": network_io.dropin,
            "drop_out": network_io.dropout,
        }

    def get_database_info(self):
        """获取数据库连接信息"""
        try:
            with connection.cursor() as cursor:
                # 获取数据库版本
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0] if cursor.rowcount > 0 else "Unknown"

                # 获取数据库大小（PostgreSQL）
                cursor.execute(
                    """
                    SELECT pg_database.datname,
                           pg_size_pretty(pg_database_size(pg_database.datname)) AS size
                    FROM pg_database
                    WHERE datname = current_database()
                """
                )
                db_size_result = cursor.fetchone()
                db_size = db_size_result[1] if db_size_result else "Unknown"

                return {
                    "version": db_version,
                    "database_name": connection.settings_dict["NAME"],
                    "size": db_size,
                    "status": "connected",
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _bytes_to_gb(self, bytes_value):
        """字节转GB"""
        return round(bytes_value / (1024**3), 2)
