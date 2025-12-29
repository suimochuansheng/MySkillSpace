#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nginx限流测试脚本（Python版本）
用途：测试AI接口、登录接口、普通API的限流效果
"""

import sys
import time
from typing import Tuple

import requests

# 配置
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"


# 颜色输出
class Colors:
    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


# 测试统计
total_tests = 0
passed_tests = 0
failed_tests = 0
test_results = []


def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_endpoint(
    name: str,
    url: str,
    method: str,
    data: dict,
    count: int,
    expected_success: int,
    expected_429: int,
) -> Tuple[int, int, int]:
    """
    测试单个endpoint的限流效果

    Args:
        name: 测试名称
        url: 测试URL
        method: HTTP方法（GET/POST）
        data: POST数据（如果是POST）
        count: 请求次数
        expected_success: 预期成功次数
        expected_429: 预期429次数

    Returns:
        (success_count, error_429_count, other_error_count)
    """
    global total_tests, passed_tests, failed_tests

    print("\n" + "-" * 60)
    print(f"测试: {name}")
    print(f"URL: {url}")
    print(f"请求次数: {count}")
    print(f"预期成功: {expected_success}, 预期429: {expected_429}")
    print("-" * 60)

    success_count = 0
    error_429_count = 0
    other_error_count = 0

    for i in range(1, count + 1):
        try:
            if method == "POST":
                response = requests.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=5,
                )
            else:
                response = requests.get(url, timeout=5)

            status_code = response.status_code

            if status_code in [200, 201, 400, 401]:
                success_count += 1
                print(f"{Colors.GREEN}✓{Colors.NC} 请求{i:2d}: {status_code}")
            elif status_code == 429:
                error_429_count += 1
                print(f"{Colors.YELLOW}⚠{Colors.NC} 请求{i:2d}: {status_code} (限流)")
            else:
                other_error_count += 1
                print(f"{Colors.RED}✗{Colors.NC} 请求{i:2d}: {status_code} (错误)")

        except requests.exceptions.RequestException as e:
            other_error_count += 1
            print(f"{Colors.RED}✗{Colors.NC} 请求{i:2d}: 请求异常 - {str(e)[:50]}")

        # 小延迟，避免瞬间全部发出
        time.sleep(0.05)

    # 结果统计
    print("\n结果统计:")
    print(f"  成功响应: {success_count}")
    print(f"  429限流: {error_429_count}")
    print(f"  其他错误: {other_error_count}")

    # 验证结果（允许±2的误差，因为网络延迟）
    total_tests += 1
    test_passed = True

    if not (expected_success - 2 <= success_count <= expected_success + 2):
        print(
            f"{Colors.RED}✗ 失败：成功次数 {success_count} 不符合预期 {expected_success}±2{Colors.NC}"
        )
        test_passed = False

    if not (expected_429 - 2 <= error_429_count <= expected_429 + 2):
        print(
            f"{Colors.RED}✗ 失败：429次数 {error_429_count} 不符合预期 {expected_429}±2{Colors.NC}"
        )
        test_passed = False

    if test_passed:
        print(f"{Colors.GREEN}✓ 测试通过{Colors.NC}")
        passed_tests += 1
        test_results.append(f"✅ {name}")
    else:
        print(f"{Colors.RED}✗ 测试失败{Colors.NC}")
        failed_tests += 1
        test_results.append(f"❌ {name}")

    # 等待限流恢复
    time.sleep(2)

    return success_count, error_429_count, other_error_count


def main():
    print_header("Nginx限流测试")
    print(f"测试目标: {BASE_URL}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # ==================== 测试1：AI接口限流 ====================
    print_header("测试1：AI接口限流（最严格）\n配置：rate=1r/s, burst=2")
    test_endpoint(
        name="AI接口限流",
        url=f"{BASE_URL}/api/ai/chat/",
        method="POST",
        data={"message": "test"},
        count=10,
        expected_success=3,
        expected_429=7,
    )

    # ==================== 测试2：登录接口限流 ====================
    print_header("测试2：登录接口限流（严格）\n配置：rate=2r/s, burst=5")
    test_endpoint(
        name="登录接口限流",
        url=f"{BASE_URL}/api/auth/login/",
        method="POST",
        data={"account": "test@example.com", "password": "test"},
        count=15,
        expected_success=7,
        expected_429=8,
    )

    # ==================== 测试3：普通API限流 ====================
    print_header("测试3：普通API限流（宽松）\n配置：rate=20r/s, burst=50")
    test_endpoint(
        name="普通API限流",
        url=f"{BASE_URL}/api/users/",
        method="GET",
        data=None,
        count=100,
        expected_success=70,
        expected_429=30,
    )

    # ==================== 测试4：静态资源（不限流） ====================
    print_header("测试4：静态资源（不限流）")
    test_endpoint(
        name="静态资源不限流",
        url=f"{BASE_URL}/favicon.ico",
        method="GET",
        data=None,
        count=20,
        expected_success=20,
        expected_429=0,
    )

    # ==================== 总结 ====================
    print_header("测试总结")
    print(f"总测试数: {total_tests}")
    print(f"{Colors.GREEN}通过: {passed_tests}{Colors.NC}")
    print(f"{Colors.RED}失败: {failed_tests}{Colors.NC}")
    print("\n测试结果详情:")
    for result in test_results:
        print(f"  {result}")

    if failed_tests == 0:
        print(f"\n{Colors.GREEN}✓ 所有测试通过！限流配置正常工作{Colors.NC}")
        return 0
    else:
        print(f"\n{Colors.RED}✗ 部分测试失败，请检查配置{Colors.NC}")
        return 1


if __name__ == "__main__":
    exit(main())
