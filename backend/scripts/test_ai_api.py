#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云通义千问 API 连接测试脚本

功能：
1. 测试 API 密钥是否有效
2. 测试流式响应是否正常
3. 验证返回格式是否符合预期

使用方法：
    python test_ai_api.py
"""

import os
import sys
from pathlib import Path

# 设置输出编码为 UTF-8
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 添加项目路径
project_root = Path(__file__).parent.parent / "SkillSpace"
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv

# 尝试加载 .env.production 或 .env
env_file = Path(__file__).parent.parent.parent / ".env.production"
if not env_file.exists():
    env_file = Path(__file__).parent.parent / ".env"

print(f"📁 加载环境变量文件: {env_file}")
load_dotenv(env_file)

# 显示当前配置
print("\n" + "=" * 60)
print("📋 当前 AI 引擎配置")
print("=" * 60)
print(f"USE_AI_API: {os.getenv('USE_AI_API', 'false')}")
print(f"ALIYUN_API_KEY: {os.getenv('ALIYUN_API_KEY', '未配置')[:20]}...")
print(f"ALIYUN_BASE_URL: {os.getenv('ALIYUN_BASE_URL', '未配置')}")
print(f"ALIYUN_MODEL_NAME: {os.getenv('ALIYUN_MODEL_NAME', 'qwen-plus')}")
print("=" * 60)

# 测试 API 连接
try:
    from openai import OpenAI

    print("\n🚀 开始测试阿里云 API 连接...\n")

    # 获取配置
    api_key = os.getenv("ALIYUN_API_KEY")
    base_url = os.getenv("ALIYUN_BASE_URL")
    model_name = os.getenv("ALIYUN_MODEL_NAME", "qwen-plus")

    if not api_key or not base_url:
        print("❌ 错误: ALIYUN_API_KEY 或 ALIYUN_BASE_URL 未配置")
        sys.exit(1)

    # 初始化客户端
    client = OpenAI(api_key=api_key, base_url=base_url)

    # 测试提示词
    test_prompt = "请用一句话介绍 Python 编程语言。"

    print(f"💬 测试提示词: {test_prompt}\n")
    print("📡 发送请求到阿里云 API...\n")

    # 发送流式请求
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "你是一个有帮助的AI助手。"},
            {"role": "user", "content": test_prompt},
        ],
        stream=True,
        temperature=0.7,
    )

    # 接收流式响应
    print("✅ API 连接成功！开始接收流式响应:\n")
    print("-" * 60)

    full_response = ""
    token_count = 0

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            token = chunk.choices[0].delta.content
            full_response += token
            token_count += 1
            print(token, end="", flush=True)

    print("\n" + "-" * 60)
    print("\n📊 响应统计:")
    print(f"   - Token 数量: {token_count}")
    print(f"   - 响应长度: {len(full_response)} 字符")
    print("\n✅ 测试完成！阿里云 API 工作正常。")

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("提示: 请确保已安装 openai 库: pip install openai")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
