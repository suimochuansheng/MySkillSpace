"""
云服务器监控配置测试脚本
测试配置文件加载和SSH连接

使用方法:
    cd /path/to/skillspace/backend/scripts
    python test_cloud_monitor.py
"""

import os
import sys

import django

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SkillSpace.settings")
django.setup()

from monitor.cloud_collectors import CloudServerCollector
from monitor.config.config_loader import get_config_loader
from monitor.utils.ssh_client import SSHClientManager


def test_config_loading():
    """测试配置文件加载"""
    print("=" * 60)
    print("测试1: 配置文件加载")
    print("=" * 60)

    try:
        config_loader = get_config_loader()
        config = config_loader.load()

        print("[OK] 配置文件加载成功")
        print(f"  配置文件版本: {config.get('version')}")

        # 获取全局配置
        global_config = config_loader.get_global_config()
        print(f"  采集间隔: {global_config.get('collect_interval')}秒")
        print(f"  SSH超时: {global_config.get('ssh_timeout')}秒")

        # 获取服务器列表
        servers = config_loader.get_servers(enabled_only=True)
        print(f"  启用的服务器数量: {len(servers)}")

        for i, server in enumerate(servers, 1):
            print(f"\n  服务器 {i}:")
            print(f"    名称: {server['name']}")
            print(
                f"    地址: {server['connection']['host']}:{server['connection']['port']}"
            )
            print(f"    用户: {server['connection']['username']}")
            print(f"    认证: {server['connection']['auth_type']}")
            print(f"    标签: {', '.join(server.get('tags', []))}")

            # 监控配置
            monitoring = server.get("monitoring", {})
            services = monitoring.get("services", [])
            print(f"    监控服务数: {len(services)}")
            if services:
                print(f"    服务列表: {', '.join([s['name'] for s in services])}")
            print(
                f"    Docker监控: {'启用' if monitoring.get('enable_docker') else '禁用'}"
            )

        return True, servers

    except Exception as e:
        print(f"[ERROR] 配置文件加载失败: {e}")
        return False, []


def test_ssh_connection(server_config):
    """测试SSH连接"""
    print("\n" + "=" * 60)
    print(f"测试2: SSH连接测试 - {server_config['name']}")
    print("=" * 60)

    connection = server_config["connection"]

    try:
        print(f"正在连接到 {connection['host']}:{connection['port']}...")

        ssh = SSHClientManager(
            host=connection["host"],
            port=connection["port"],
            username=connection["username"],
            password=connection.get("password"),
            key_path=connection.get("private_key_path"),
            timeout=10,
        )

        # 建立连接
        ssh.connect()
        print("[OK] SSH连接成功")

        # 测试基本命令
        print("\n执行测试命令:")

        # 1. 测试 uname
        result = ssh.execute_command("uname -a")
        print(f"  系统信息: {result['stdout'][:80]}...")

        # 2. 测试 hostname
        result = ssh.execute_command("hostname")
        print(f"  主机名: {result['stdout']}")

        # 3. 测试 uptime
        result = ssh.execute_command("uptime -p")
        print(f"  运行时间: {result['stdout']}")

        # 关闭连接
        ssh.close()
        print("\n[OK] SSH连接测试通过")
        return True, ssh

    except Exception as e:
        print(f"\n[ERROR] SSH连接失败: {e}")
        return False, None


def test_data_collection(server_config):
    """测试数据采集"""
    print("\n" + "=" * 60)
    print(f"测试3: 数据采集测试 - {server_config['name']}")
    print("=" * 60)

    connection = server_config["connection"]

    try:
        # 创建SSH连接
        ssh = SSHClientManager(
            host=connection["host"],
            port=connection["port"],
            username=connection["username"],
            password=connection.get("password"),
            key_path=connection.get("private_key_path"),
        )
        ssh.connect()

        # 创建数据采集器
        collector = CloudServerCollector(ssh)

        # 采集各类数据
        print("\n1. 采集系统信息...")
        system_info = collector.collect_system_info()
        print(f"   [OK] 主机名: {system_info.get('hostname')}")
        print(f"   [OK] 运行时间: {system_info.get('uptime')}")

        print("\n2. 采集CPU信息...")
        cpu_info = collector.collect_cpu_info()
        print(f"   [OK] CPU使用率: {cpu_info.get('usage_percent')}%")
        print(f"   [OK] CPU核心数: {cpu_info.get('cores')}")
        print(
            f"   [OK] 负载平均: {cpu_info.get('load_avg_1')}, {cpu_info.get('load_avg_5')}, {cpu_info.get('load_avg_15')}"
        )

        print("\n3. 采集内存信息...")
        memory_info = collector.collect_memory_info()
        total_gb = memory_info.get("total", 0) / (1024**3)
        used_gb = memory_info.get("used", 0) / (1024**3)
        print(f"   [OK] 总内存: {total_gb:.2f} GB")
        print(f"   [OK] 已用内存: {used_gb:.2f} GB")
        print(f"   [OK] 内存使用率: {memory_info.get('usage_percent')}%")

        print("\n4. 采集磁盘信息...")
        disk_info = collector.collect_disk_info()
        total_gb = disk_info.get("total", 0) / (1024**3)
        used_gb = disk_info.get("used", 0) / (1024**3)
        print(f"   [OK] 总磁盘: {total_gb:.2f} GB")
        print(f"   [OK] 已用磁盘: {used_gb:.2f} GB")
        print(f"   [OK] 磁盘使用率: {disk_info.get('usage_percent')}%")

        print("\n5. 采集网络信息...")
        network_info = collector.collect_network_info()
        recv_gb = network_info.get("bytes_recv", 0) / (1024**3)
        sent_gb = network_info.get("bytes_sent", 0) / (1024**3)
        print(f"   [OK] 接收流量: {recv_gb:.2f} GB")
        print(f"   [OK] 发送流量: {sent_gb:.2f} GB")

        # 测试服务检查
        monitoring = server_config.get("monitoring", {})
        services = monitoring.get("services", [])

        if services:
            print(f"\n6. 检查服务状态 ({len(services)}个服务)...")
            for service_config in services[:3]:  # 只测试前3个
                service_data = collector.check_service(service_config)
                status_icon = "[OK]" if service_data["status"] == "running" else "[X]"
                print(
                    f"   {status_icon} {service_data['name']}: {service_data['status']}"
                )

        # 测试Docker容器
        if monitoring.get("enable_docker"):
            print("\n7. 采集Docker容器信息...")
            containers = collector.collect_docker_containers()
            if containers:
                print(f"   [OK] 发现 {len(containers)} 个容器")
                for container in containers[:3]:  # 只显示前3个
                    print(f"     - {container['name']}: {container['status']}")
            else:
                print("   [INFO] 未发现运行中的容器或Docker未安装")

        ssh.close()
        print("\n[OK] 数据采集测试通过")
        return True

    except Exception as e:
        print(f"\n[ERROR] 数据采集失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "云服务器监控配置测试" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # 测试1: 配置文件加载
    success, servers = test_config_loading()
    if not success or not servers:
        print("\n测试终止：配置文件加载失败")
        return

    # 对每个启用的服务器进行测试
    for server in servers:
        # 测试2: SSH连接
        success, _ = test_ssh_connection(server)
        if not success:
            print(f"\n跳过服务器 {server['name']} 的数据采集测试")
            continue

        # 测试3: 数据采集
        test_data_collection(server)

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n如果所有测试通过，你可以启动Django服务器:")
    print("  python manage.py runserver")
    print("\n云监控WebSocket地址:")
    for server in servers:
        print(f"  ws://localhost:8000/ws/monitor/cloud/{server['name']}/")
    print()


if __name__ == "__main__":
    main()
