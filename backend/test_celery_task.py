"""
Celery 任务队列测试脚本 - 测试1: 验证任务是否正常执行

使用方法:
1. 确保 RabbitMQ 已启动
2. 确保 Celery Worker 已启动:
   celery -A SkillSpace worker -Q gpu_queue -l info
3. 运行此脚本:
   cd E:\skillSpace\backend
   sk_venv\Scripts\python test_celery_task.py
"""

import os
import sys
import django
import time

# 设置Django环境
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkillSpace.settings')
django.setup()

from SkillSpace.myapps.ai_demo.tasks import qwen_chat_task
from celery.result import AsyncResult


def test_single_task():
    """测试单个任务"""
    print("\n" + "="*60)
    print("📝 测试1: 提交单个AI任务到gpu_queue队列")
    print("="*60)

    prompt = "请用一句话介绍Python编程语言"

    print(f"\n✅ 提交任务: {prompt}")
    task = qwen_chat_task.delay(prompt)

    print(f"📌 任务ID: {task.id}")
    print(f"📌 任务状态: {task.state}")
    print(f"📌 任务队列: gpu_queue (自动路由)")

    print("\n⏳ 等待任务执行...")
    start_time = time.time()

    # 轮询任务状态
    while not task.ready():
        print(f"  状态: {task.state} - 已等待 {time.time() - start_time:.1f} 秒")
        time.sleep(2)

    end_time = time.time()

    print(f"\n✅ 任务完成! 耗时: {end_time - start_time:.2f} 秒")
    print(f"📌 最终状态: {task.state}")

    if task.successful():
        result = task.result
        print(f"\n✅ 任务结果:")
        print(f"  状态: {result.get('status')}")
        print(f"  回答: {result.get('result')[:200]}...")  # 只显示前200字符
    else:
        print(f"\n❌ 任务失败: {task.info}")


def test_multiple_tasks():
    """测试多任务排队"""
    print("\n" + "="*60)
    print("📝 测试2: 提交多个任务测试队列排队效果")
    print("="*60)

    prompts = [
        "什么是机器学习?",
        "什么是深度学习?",
        "什么是神经网络?",
    ]

    tasks = []

    print(f"\n✅ 批量提交 {len(prompts)} 个任务到队列...")
    for i, prompt in enumerate(prompts, 1):
        task = qwen_chat_task.delay(prompt)
        tasks.append((task, prompt))
        print(f"  [{i}] 任务ID: {task.id} - 问题: {prompt}")

    print(f"\n📌 所有任务已提交到 gpu_queue 队列")
    print(f"📌 Worker配置: prefetch_multiplier=1 (一次只处理1个)")
    print(f"📌 预期行为: 任务会按顺序排队执行，不会并发\n")

    # 监控所有任务
    completed = 0
    while completed < len(tasks):
        time.sleep(2)
        for i, (task, prompt) in enumerate(tasks, 1):
            status_symbol = "✅" if task.ready() else "⏳"
            print(f"  [{i}] {status_symbol} {task.state:10s} | {prompt}")

        completed = sum(1 for task, _ in tasks if task.ready())
        print(f"\n进度: {completed}/{len(tasks)} 完成\n")

    print("\n" + "="*60)
    print("✅ 所有任务执行完毕!")
    print("="*60)

    # 显示结果
    for i, (task, prompt) in enumerate(tasks, 1):
        if task.successful():
            result = task.result
            print(f"\n[{i}] {prompt}")
            print(f"    回答: {result.get('result')[:100]}...")


def test_task_inspection():
    """测试任务状态查询"""
    print("\n" + "="*60)
    print("📝 测试3: 查询队列状态和活跃任务")
    print("="*60)

    from celery import current_app

    # 获取Celery应用实例
    app = current_app

    print("\n✅ 查询Worker状态...")
    inspect = app.control.inspect()

    # 活跃任务
    active_tasks = inspect.active()
    if active_tasks:
        print("\n📌 活跃任务 (正在执行):")
        for worker, tasks in active_tasks.items():
            print(f"  Worker: {worker}")
            for task in tasks:
                print(f"    - {task['name']} (ID: {task['id']})")
    else:
        print("\n📌 当前无活跃任务")

    # 预留任务
    reserved_tasks = inspect.reserved()
    if reserved_tasks:
        print("\n📌 预留任务 (队列中等待):")
        for worker, tasks in reserved_tasks.items():
            print(f"  Worker: {worker}")
            for task in tasks:
                print(f"    - {task['name']} (ID: {task['id']})")
    else:
        print("\n📌 队列中无等待任务")

    # Worker统计
    stats = inspect.stats()
    if stats:
        print("\n📌 Worker统计信息:")
        for worker, stat in stats.items():
            print(f"  Worker: {worker}")
            print(f"    总任务数: {stat.get('total', {})}")
            print(f"    活跃进程: {stat.get('pool', {}).get('max-concurrency', 'N/A')}")


def main():
    """主测试函数"""
    print("\n🚀 开始 Celery 任务队列测试")
    print("⚠️  请确保已启动:")
    print("   1. RabbitMQ 服务")
    print("   2. Celery Worker: celery -A SkillSpace worker -Q gpu_queue -l info")

    input("\n按回车键继续...")

    try:
        # 测试1: 单任务
        test_single_task()

        input("\n按回车键继续下一个测试...")

        # 测试2: 多任务
        test_multiple_tasks()

        input("\n按回车键继续下一个测试...")

        # 测试3: 状态查询
        test_task_inspection()

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n✅ 测试完成!")


if __name__ == "__main__":
    main()
