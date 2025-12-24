"""
云服务器数据采集器
通过SSH远程执行命令采集Linux服务器的系统数据
"""

import logging
import re
from typing import Dict, List, Optional

from .utils.ssh_client import SSHClientManager

logger = logging.getLogger(__name__)


class CloudServerCollector:
    """云服务器数据采集器"""

    def __init__(self, ssh_client: SSHClientManager):
        """
        初始化数据采集器

        Args:
            ssh_client: SSH客户端管理器实例
        """
        self.ssh = ssh_client

    def collect_all(self) -> Dict:
        """
        采集所有数据

        Returns:
            包含所有监控数据的字典
        """
        data = {
            "system": self.collect_system_info(),
            "cpu": self.collect_cpu_info(),
            "memory": self.collect_memory_info(),
            "disk": self.collect_disk_info(),
            "network": self.collect_network_info(),
            "services": [],  # 服务状态由外部调用check_service添加
            "containers": [],  # Docker容器由外部调用collect_docker_containers添加
        }
        return data

    def collect_system_info(self) -> Dict:
        """
        采集系统基本信息

        Returns:
            系统信息字典
        """
        try:
            # 获取系统信息
            uname_result = self.ssh.execute_command("uname -a")
            uname = uname_result["stdout"]

            # 获取主机名
            hostname_result = self.ssh.execute_command("hostname")
            hostname = hostname_result["stdout"]

            # 获取运行时间
            uptime_result = self.ssh.execute_command("uptime -p")
            uptime = uptime_result["stdout"]

            # 获取系统启动时间
            boot_time_result = self.ssh.execute_command("uptime -s")
            boot_time = boot_time_result["stdout"]

            return {
                "platform": "Linux",
                "hostname": hostname,
                "kernel": uname,
                "uptime": uptime,
                "boot_time": boot_time,
            }
        except Exception as e:
            logger.error(f"采集系统信息失败: {e}")
            return {
                "platform": "Linux",
                "hostname": "Unknown",
                "kernel": "Unknown",
                "uptime": "Unknown",
                "boot_time": "Unknown",
            }

    def collect_cpu_info(self) -> Dict:
        """
        采集CPU信息

        Returns:
            CPU信息字典
        """
        try:
            # CPU使用率（100 - idle%）
            cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
            cpu_result = self.ssh.execute_command(cpu_cmd)
            cpu_usage_str = cpu_result["stdout"]
            cpu_usage = float(cpu_usage_str) if cpu_usage_str else 0.0

            # CPU核心数
            cores_cmd = "nproc"
            cores_result = self.ssh.execute_command(cores_cmd)
            cpu_cores = int(cores_result["stdout"]) if cores_result["stdout"] else 0

            # 负载平均值
            load_cmd = "uptime | awk -F'load average:' '{print $2}'"
            load_result = self.ssh.execute_command(load_cmd)
            load_avg_str = load_result["stdout"].strip()

            # 解析负载平均值（格式：0.00, 0.00, 0.00）
            load_avg = [0.0, 0.0, 0.0]
            if load_avg_str:
                load_parts = [x.strip() for x in load_avg_str.split(",")]
                for i, part in enumerate(load_parts[:3]):
                    try:
                        load_avg[i] = float(part)
                    except ValueError:
                        pass

            return {
                "usage_percent": round(cpu_usage, 2),
                "cores": cpu_cores,
                "load_avg_1": round(load_avg[0], 2),
                "load_avg_5": round(load_avg[1], 2),
                "load_avg_15": round(load_avg[2], 2),
            }
        except Exception as e:
            logger.error(f"采集CPU信息失败: {e}")
            return {
                "usage_percent": 0.0,
                "cores": 0,
                "load_avg_1": 0.0,
                "load_avg_5": 0.0,
                "load_avg_15": 0.0,
            }

    def collect_memory_info(self) -> Dict:
        """
        采集内存信息

        Returns:
            内存信息字典
        """
        try:
            # 使用free命令获取内存信息（字节）
            # 输出格式：total used free available
            mem_cmd = "free -b | awk 'NR==2{printf \"%s %s %s %s\", $2, $3, $4, $7}'"
            mem_result = self.ssh.execute_command(mem_cmd)
            mem_parts = mem_result["stdout"].split()

            if len(mem_parts) >= 4:
                total = int(mem_parts[0])
                used = int(mem_parts[1])
                free = int(mem_parts[2])
                available = int(mem_parts[3])

                usage_percent = (used / total * 100) if total > 0 else 0.0

                # 获取Swap信息
                swap_cmd = "free -b | awk 'NR==3{printf \"%s %s %s\", $2, $3, $4}'"
                swap_result = self.ssh.execute_command(swap_cmd)
                swap_parts = swap_result["stdout"].split()

                swap_total = int(swap_parts[0]) if len(swap_parts) > 0 else 0
                swap_used = int(swap_parts[1]) if len(swap_parts) > 1 else 0
                swap_free = int(swap_parts[2]) if len(swap_parts) > 2 else 0
                swap_percent = (swap_used / swap_total * 100) if swap_total > 0 else 0.0

                return {
                    "total": total,
                    "used": used,
                    "free": free,
                    "available": available,
                    "usage_percent": round(usage_percent, 2),
                    "swap_total": swap_total,
                    "swap_used": swap_used,
                    "swap_free": swap_free,
                    "swap_percent": round(swap_percent, 2),
                }
        except Exception as e:
            logger.error(f"采集内存信息失败: {e}")

        return {
            "total": 0,
            "used": 0,
            "free": 0,
            "available": 0,
            "usage_percent": 0.0,
            "swap_total": 0,
            "swap_used": 0,
            "swap_free": 0,
            "swap_percent": 0.0,
        }

    def collect_disk_info(self) -> Dict:
        """
        采集磁盘信息

        Returns:
            磁盘信息字典
        """
        try:
            # 获取根分区磁盘使用情况（字节）
            # 输出格式：total used free usage%
            disk_cmd = "df -B1 / | awk 'NR==2{printf \"%s %s %s %s\", $2, $3, $4, $5}'"
            disk_result = self.ssh.execute_command(disk_cmd)
            disk_parts = disk_result["stdout"].split()

            if len(disk_parts) >= 4:
                total = int(disk_parts[0])
                used = int(disk_parts[1])
                free = int(disk_parts[2])
                usage_str = disk_parts[3].rstrip("%")
                usage_percent = float(usage_str)

                # 获取所有分区信息
                partitions_cmd = "df -h | awk 'NR>1 && $1 ~ /^\\/dev\\// {printf \"%s|%s|%s|%s|%s\\n\", $1, $2, $3, $4, $5}'"
                partitions_result = self.ssh.execute_command(partitions_cmd)

                partitions = []
                for line in partitions_result["stdout"].split("\n"):
                    if line.strip():
                        parts = line.split("|")
                        if len(parts) >= 5:
                            partitions.append(
                                {
                                    "device": parts[0],
                                    "total": parts[1],
                                    "used": parts[2],
                                    "free": parts[3],
                                    "usage_percent": parts[4],
                                }
                            )

                return {
                    "total": total,
                    "used": used,
                    "free": free,
                    "usage_percent": usage_percent,
                    "partitions": partitions,
                }
        except Exception as e:
            logger.error(f"采集磁盘信息失败: {e}")

        return {
            "total": 0,
            "used": 0,
            "free": 0,
            "usage_percent": 0.0,
            "partitions": [],
        }

    def collect_network_info(self) -> Dict:
        """
        采集网络信息

        Returns:
            网络信息字典
        """
        try:
            # 获取网络流量（从/proc/net/dev）
            # 匹配eth0、ens、enp等常见网络接口
            net_cmd = "cat /proc/net/dev | grep -E '(eth0|ens|enp)' | head -1 | awk '{print $2, $10}'"
            net_result = self.ssh.execute_command(net_cmd)
            net_parts = net_result["stdout"].split()

            if len(net_parts) >= 2:
                recv_bytes = int(net_parts[0])
                sent_bytes = int(net_parts[1])

                return {
                    "bytes_recv": recv_bytes,
                    "bytes_sent": sent_bytes,
                }
        except Exception as e:
            logger.error(f"采集网络信息失败: {e}")

        return {
            "bytes_recv": 0,
            "bytes_sent": 0,
        }

    def check_service(self, service_config: Dict) -> Dict:
        """
        检查服务状态

        Args:
            service_config: 服务配置字典，包含name、type、process_pattern等

        Returns:
            服务状态字典
        """
        service_name = service_config["name"]
        process_pattern = service_config.get("process_pattern", service_name)
        service_type = service_config.get("type", "other")
        port = service_config.get("port")

        try:
            # 检查进程是否运行
            ps_cmd = f"ps aux | grep '{process_pattern}' | grep -v grep | head -1"
            ps_result = self.ssh.execute_command(ps_cmd)

            is_running = bool(ps_result["stdout"])
            process_info = ps_result["stdout"][:200] if is_running else None

            # 如果有端口配置，检查端口是否监听
            port_listening = False
            if port:
                port_cmd = f"netstat -tlnp 2>/dev/null | grep ':{port}' || ss -tlnp | grep ':{port}'"
                port_result = self.ssh.execute_command(port_cmd)
                port_listening = bool(port_result["stdout"])

            # 获取CPU和内存使用（如果进程运行中）
            cpu_usage = None
            memory_usage = None
            if is_running and process_info:
                # 尝试从ps输出中提取CPU和内存
                try:
                    parts = process_info.split()
                    if len(parts) >= 4:
                        cpu_usage = float(parts[2])  # CPU%
                        memory_usage = float(parts[3])  # MEM%
                except Exception as e:
                    pass

            return {
                "name": service_name,
                "type": service_type,
                "status": "running" if is_running else "stopped",
                "port": port,
                "port_listening": port_listening if port else None,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "process_info": process_info,
            }

        except Exception as e:
            logger.error(f"检查服务失败 {service_name}: {e}")
            return {
                "name": service_name,
                "type": service_type,
                "status": "error",
                "error": str(e),
            }

    def collect_docker_containers(self) -> List[Dict]:
        """
        采集Docker容器信息

        Returns:
            容器信息列表
        """
        try:
            # 检查Docker是否安装
            docker_check = self.ssh.execute_command("which docker")
            if not docker_check["stdout"]:
                logger.debug("Docker未安装或不可用")
                return []

            # 获取容器列表
            # 格式：name|status|image|created
            docker_cmd = "docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}|{{.CreatedAt}}'"
            docker_result = self.ssh.execute_command(docker_cmd)

            containers = []
            for line in docker_result["stdout"].split("\n"):
                if line.strip():
                    parts = line.split("|")
                    if len(parts) >= 3:
                        # 解析状态（Up 2 hours 或 Exited (0) 2 hours ago）
                        status_str = parts[1]
                        is_running = status_str.startswith("Up")

                        containers.append(
                            {
                                "name": parts[0],
                                "status": "running" if is_running else "stopped",
                                "status_detail": status_str,
                                "image": parts[2],
                                "created": parts[3] if len(parts) > 3 else None,
                            }
                        )

            # 如果有运行中的容器，获取资源使用情况
            if containers:
                try:
                    stats_cmd = "docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}'"
                    stats_result = self.ssh.execute_command(stats_cmd, timeout=10)

                    # 将资源使用情况添加到容器信息中
                    stats_dict = {}
                    for line in stats_result["stdout"].split("\n"):
                        if line.strip():
                            parts = line.split("|")
                            if len(parts) >= 3:
                                stats_dict[parts[0]] = {
                                    "cpu_percent": parts[1],
                                    "memory_usage": parts[2],
                                }

                    # 合并资源使用信息
                    for container in containers:
                        if container["name"] in stats_dict:
                            container.update(stats_dict[container["name"]])
                except Exception as e:
                    logger.debug("获取Docker容器资源使用失败")

            return containers

        except Exception as e:
            logger.error(f"采集Docker容器失败: {e}")
            return []

    def test_connection(self) -> bool:
        """
        测试SSH连接是否正常

        Returns:
            连接正常返回True，否则返回False
        """
        try:
            result = self.ssh.execute_command("echo 'test'", timeout=5)
            return result["exit_code"] == 0
        except Exception as e:
            return False
