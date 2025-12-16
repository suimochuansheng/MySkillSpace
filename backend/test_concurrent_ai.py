"""
并发访问测试脚本 - 测试2: 模拟多用户同时访问AI接口

使用方法:
1. 确保Django服务已启动: python manage.py runserver
2. 运行此脚本:
   cd E:\skillSpace\backend
   sk_venv\Scripts\python test_concurrent_ai.py
"""

import requests
import threading
import time
from datetime import datetime


# 配置
API_URL = "http://127.0.0.1:8000/api/ai/qwen/"
SESSION_ID = "test_concurrent_session"
NUM_REQUESTS = 3  # 并发请求数


def send_ai_request(user_id, prompt):
    """发送AI对话请求"""
    print(f"[用户{user_id}] {datetime.now().strftime('%H:%M:%S')} 开始发送请求...")

    start_time = time.time()

    try:
        # 发送POST请求（非流式，便于测试）
        response = requests.post(
            API_URL,
            json={
                "prompt": prompt,
                "session_id": f"{SESSION_ID}_{user_id}",
                "stream": False  # 关闭流式，使用阻塞模式便于测试
            },
            timeout=120  # 2分钟超时
        )

        end_time = time.time()
        duration = end_time - start_time

        if response.status_code == 200:
            result = response.json()
            answer_length = len(result.get('data', ''))
            print(f"[用户{user_id}] ✅ 请求成功! 耗时: {duration:.2f}秒, 回答长度: {answer_length}字符")
            print(f"[用户{user_id}] 回答预览: {result.get('data', '')[:100]}...")
        else:
            print(f"[用户{user_id}] ❌ 请求失败! 状态码: {response.status_code}")

    except requests.Timeout:
        print(f"[用户{user_id}] ⏰ 请求超时!")
    except Exception as e:
        print(f"[用户{user_id}] ❌ 请求异常: {str(e)}")


def test_concurrent_requests():
    """测试并发请求"""
    print("\n" + "="*70)
    print("🚀 并发访问测试 - 模拟多用户同时访问AI接口")
    print("="*70)

    print(f"\n📌 配置:")
    print(f"   API地址: {API_URL}")
    print(f"   并发用户数: {NUM_REQUESTS}")
    print(f"   请求模式: 非流式(阻塞模式)")

    print(f"\n⚠️  预期行为:")
    print(f"   - 如果views.py使用同步调用: 请求会串行执行，耗时累加")
    print(f"   - 如果使用信号量控制: 请求会排队，但每个都会执行")
    print(f"   - 如果使用Celery: 需要轮询任务状态(当前脚本不支持)")

    input("\n按回车键开始测试...")

    # 准备测试问题
    prompts = [
        "什么是Python?",
        "什么是Django?",
        "什么是机器学习?",
    ]

    threads = []

    print(f"\n✅ 启动 {NUM_REQUESTS} 个并发线程...")
    print(f"📌 开始时间: {datetime.now().strftime('%H:%M:%S')}\n")

    global_start = time.time()

    # 创建并启动线程
    for i in range(NUM_REQUESTS):
        user_id = i + 1
        prompt = prompts[i % len(prompts)]
        thread = threading.Thread(target=send_ai_request, args=(user_id, prompt))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # 略微错开启动时间

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    global_end = time.time()
    total_duration = global_end - global_start

    print(f"\n" + "="*70)
    print(f"✅ 所有请求完成!")
    print(f"📌 结束时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📌 总耗时: {total_duration:.2f}秒")
    print(f"📌 平均耗时: {total_duration/NUM_REQUESTS:.2f}秒/请求")
    print("="*70)

    print(f"\n📊 性能分析:")
    if total_duration < NUM_REQUESTS * 2:
        print(f"   ✅ 请求可能是并行处理的 (总耗时 < {NUM_REQUESTS * 2}秒)")
    else:
        print(f"   ⚠️  请求可能是串行处理的 (总耗时 ≈ {NUM_REQUESTS} * 单次耗时)")
        print(f"   建议: 添加队列控制或使用Celery异步任务")


def test_stream_request():
    """测试流式请求（SSE）"""
    print("\n" + "="*70)
    print("🚀 流式请求测试 - 测试SSE实时输出")
    print("="*70)

    print(f"\n📌 发送流式请求...")

    try:
        response = requests.post(
            API_URL,
            json={
                "prompt": "请简单介绍一下人工智能",
                "session_id": "test_stream",
                "stream": True
            },
            stream=True,  # 启用流式接收
            timeout=120
        )

        if response.status_code == 200:
            print(f"\n✅ 流式连接建立成功，开始接收数据...\n")

            token_count = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        import json
                        data = json.loads(line_str[6:])  # 去掉 "data: " 前缀

                        token = data.get('token', '')
                        token_type = data.get('type', '')

                        if token:
                            print(token, end='', flush=True)
                            token_count += 1

                        if token_type == 'finish':
                            print(f"\n\n✅ 流式输出完成! 共接收 {token_count} 个token")
                            break
        else:
            print(f"❌ 请求失败! 状态码: {response.status_code}")

    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")


def main():
    """主测试函数"""
    print("\n🚀 AI接口并发测试工具")
    print("⚠️  请确保Django服务已启动: python manage.py runserver")

    while True:
        print("\n" + "="*70)
        print("请选择测试类型:")
        print("  1. 并发请求测试 (多用户同时访问)")
        print("  2. 流式请求测试 (SSE实时输出)")
        print("  3. 退出")
        print("="*70)

        choice = input("\n请输入选择 (1/2/3): ").strip()

        if choice == '1':
            test_concurrent_requests()
        elif choice == '2':
            test_stream_request()
        elif choice == '3':
            print("\n👋 再见!")
            break
        else:
            print("\n❌ 无效选择，请重试")


if __name__ == "__main__":
    main()
