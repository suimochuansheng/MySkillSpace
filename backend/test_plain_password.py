"""
测试开发环境明文密码功能

此脚本用于验证在开发环境下明文密码是否正确保存
"""

import os
import sys
import django

# 设置输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkillSpace.settings')
django.setup()

from auth_system.models import User
from django.conf import settings

def test_plain_password():
    """测试明文密码功能"""

    print("=" * 60)
    print("开发环境明文密码功能测试")
    print("=" * 60)

    # 检查是否为开发环境
    print(f"\n1. 环境检查:")
    print(f"   DEBUG 模式: {settings.DEBUG}")

    if not settings.DEBUG:
        print("   警告：当前不是开发环境，明文密码功能已禁用")
        return

    # 创建测试用户
    print(f"\n2. 创建测试用户:")
    test_email = "test_plain_password@example.com"
    test_password = "TestPass123"

    # 删除已存在的测试用户
    User.objects.filter(email=test_email).delete()

    # 创建新用户
    user = User.objects.create_user(
        email=test_email,
        username="测试用户",
        password=test_password
    )

    print(f"   [OK] 用户已创建: {user.email}")
    print(f"   [OK] 用户名: {user.username}")

    # 验证密码加密
    print(f"\n3. 密码验证:")
    print(f"   加密密码 (password): {user.password[:50]}...")
    print(f"   明文密码 (plain_password): {user.plain_password}")

    # 验证密码是否正确加密
    is_password_encrypted = user.check_password(test_password)
    print(f"   [OK] 密码加密验证: {'通过' if is_password_encrypted else '失败'}")

    # 验证明文密码是否保存
    is_plain_password_saved = user.plain_password == test_password
    print(f"   [OK] 明文密码保存: {'通过' if is_plain_password_saved else '失败'}")

    # 查询所有用户的明文密码情况
    print(f"\n4. 所有用户明文密码状态:")
    all_users = User.objects.all()
    print(f"   总用户数: {all_users.count()}")

    for u in all_users:
        status = "[已保存]" if u.plain_password else "[未保存-旧用户]"
        print(f"   - {u.email}: {status}")
        if u.plain_password:
            print(f"     明文密码: {u.plain_password}")

    # 清理测试用户
    print(f"\n5. 清理测试数据:")
    user.delete()
    print(f"   [OK] 测试用户已删除")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 访问 http://127.0.0.1:8000/admin/auth_system/user/")
    print("2. 在用户列表中可以看到 '明文密码 (开发用)' 列")
    print("3. 创建新用户时，明文密码会自动保存")
    print("4. 编辑用户时，可以在 '开发调试' 折叠区域查看明文密码")
    print("\n重要提示:")
    print("- 此功能仅用于开发环境调试")
    print("- 生产环境部署时请将 DEBUG 设为 False")
    print("- 生产环境应删除 plain_password 字段")

if __name__ == "__main__":
    test_plain_password()
