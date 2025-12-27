#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP地理位置查询功能测试脚本
测试 get_ip_location 函数是否正常工作
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent / "SkillSpace"
sys.path.insert(0, str(project_root))

# 导入测试函数
from myapps.auth_system.log_utils import get_ip_location

# 测试用例
test_cases = [
    ("8.8.8.8", "Google DNS - 美国"),
    ("114.114.114.114", "国内DNS - 中国"),
    ("127.0.0.1", "本地IP"),
    ("192.168.1.1", "内网IP"),
    ("47.108.123.45", "阿里云服务器示例"),
    ("", "空IP"),
]

print("=" * 60)
print("IP地理位置查询功能测试")
print("=" * 60)
print()

for ip, description in test_cases:
    print(f"测试: {description}")
    print(f"IP地址: {ip or '(空)'}")

    try:
        location = get_ip_location(ip)
        print(f"地理位置: {location}")
        print("✅ 成功")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("-" * 60)
    print()

print("=" * 60)
print("测试完成！")
print()
print("说明：")
print("- 本地IP (127.0.0.1): 显示为'本地'")
print("- 内网IP (192.168.x.x, 10.x.x.x): 显示为'内网IP'")
print("- 公网IP: 查询IP-API.com获取地理位置")
print("- 查询超时: 3秒超时保护")
print("- 免费限制: 每分钟45次请求")
print("=" * 60)
