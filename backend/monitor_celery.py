"""
Celery 监控脚本 - 实时查看队列和任务状态

使用方法:
  单次查询: python monitor_celery.py
  持续监控: python monitor_celery.py --watch
"""

import os
import sys
import django
from datetime import datetime
import time

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkillSpace.settings')
django.setup()

from celery import current_app


def print_header(title):
    """打印标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def monitor_queues():
    """监控队列状态"""
    app = current_app
    inspect = app.control.inspect()

    print_header(f"📊 Celery 队列监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Worker状态
    stats = inspect.stats()
    if stats:
        print("🖥️  Worker 状态:")
        for worker, stat in stats.items():
            total_tasks = stat.get('total', {})
            print(f"  ✅ {worker}")
            print(f"     总任务数: {total_tasks}")
            print(f"     进程池: {stat.get('pool', {}).get('max-concurrency', 'N/A')}")
            print(f"     预取数: {stat.get('prefetch_count', 'N/A')}")
    else:
        print("❌ 没有活跃的Worker!")
        print("   请先启动Worker: celery -A SkillSpace worker -Q gpu_queue -l info")
        return

    # 2. 活跃任务
    active = inspect.active()
    print(f"\n⚡ 活跃任务 (正在执行):")
    active_count = 0
    if active and any(active.values()):
        for worker, tasks in active.items():
            if tasks:
                print(f"  Worker: {worker}")
                for task in tasks:
                    active_count += 1
                    print(f"    🔄 {task['name']}")
                    print(f"       ID: {task['id'][:8]}...")
                    print(f"       参数: {task.get('args', [])}")
                    print(f"       开始时间: {task.get('time_start', 'N/A')}")
    else:
        print("  (无活跃任务)")

    # 3. 预留任务
    reserved = inspect.reserved()
    print(f"\n📋 预留任务 (队列中等待):")
    reserved_count = 0
    if reserved and any(reserved.values()):
        for worker, tasks in reserved.items():
            if tasks:
                print(f"  Worker: {worker}")
                for task in tasks:
                    reserved_count += 1
                    print(f"    ⏳ {task['name']}")
                    print(f"       ID: {task['id'][:8]}...")
    else:
        print("  (无等待任务)")

    # 4. 活跃队列
    active_queues = inspect.active_queues()
    print(f"\n📂 活跃队列:")
    if active_queues:
        for worker, queues in active_queues.items():
            print(f"  Worker: {worker}")
            for queue in queues:
                print(f"    📥 {queue['name']}")
                print(f"       路由键: {queue.get('routing_key', 'N/A')}")
    else:
        print("  (无活跃队列)")

    # 5. 已注册任务
    registered = inspect.registered()
    print(f"\n📝 已注册任务:")
    if registered:
        for worker, tasks in registered.items():
            custom_tasks = [t for t in tasks if 'myapps' in t]
            if custom_tasks:
                print(f"  Worker: {worker}")
                for task in custom_tasks:
                    # 判断任务路由
                    if 'ai_demo' in task:
                        queue_info = "→ gpu_queue"
                    elif 'resume' in task:
                        queue_info = "→ api_queue"
                    else:
                        queue_info = "→ default"

                    print(f"    ✓ {task} {queue_info}")

    # 6. 统计汇总
    print(f"\n📊 统计汇总:")
    print(f"  活跃任务数: {active_count}")
    print(f"  等待任务数: {reserved_count}")
    print(f"  总待处理: {active_count + reserved_count}")


def continuous_monitor():
    """持续监控模式"""
    print("🚀 启动持续监控模式 (按Ctrl+C停止)\n")

    try:
        while True:
            # 清屏 (Windows)
            os.system('cls' if os.name == 'nt' else 'clear')

            monitor_queues()

            print("\n⏰ 下次刷新: 5秒后...")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n✅ 监控已停止")


def check_health():
    """健康检查"""
    print_header("🏥 Celery 健康检查")

    app = current_app
    inspect = app.control.inspect()

    # 检查Worker状态
    stats = inspect.stats()
    if not stats:
        print("❌ Worker未运行")
        print("\n启动命令:")
        print("  celery -A SkillSpace worker -Q gpu_queue,api_queue,default -l info")
        return False

    # 检查队列配置
    from SkillSpace.celery_demo import app as celery_app
    queues = celery_app.conf.task_queues

    print("✅ Celery应用配置:")
    print(f"  Broker: {celery_app.conf.broker_url}")
    print(f"  配置的队列数: {len(queues)}")
    for queue in queues:
        print(f"    - {queue.name} (优先级: {queue.priority})")

    print("\n✅ Worker状态:")
    for worker in stats.keys():
        print(f"  - {worker}")

    print("\n✅ 健康检查通过!")
    return True


def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--watch':
            continuous_monitor()
        elif sys.argv[1] == '--health':
            check_health()
        else:
            print("用法:")
            print("  python monitor_celery.py           # 单次查询")
            print("  python monitor_celery.py --watch   # 持续监控")
            print("  python monitor_celery.py --health  # 健康检查")
    else:
        monitor_queues()
        print("\n💡 提示:")
        print("  使用 'python monitor_celery.py --watch' 启用持续监控")
        print("  使用 'python monitor_celery.py --health' 运行健康检查")


if __name__ == "__main__":
    main()
