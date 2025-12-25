"""
修复通过Django Admin创建的用户密码问题
如果在admin中直接设置密码字段，密码不会被加密，导致无法登录

使用方法:
    cd /path/to/skillspace/backend/scripts
    python fix_passwords.py
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

from auth_system.models import User


def check_and_fix_passwords():
    """检查并修复所有明文密码用户"""
    print("=" * 60)
    print("🔍 Django用户密码检查和修复工具")
    print("=" * 60)

    users = User.objects.all()
    total_users = users.count()

    if total_users == 0:
        print("⚠️ 数据库中没有用户")
        return

    print(f"📊 共找到 {total_users} 个用户\n")

    fixed_count = 0
    normal_count = 0

    for user in users:
        print(f"检查用户: {user.email} ({user.username})")

        # Django加密密码格式: algorithm$iterations$salt$hash
        # 例如: pbkdf2_sha256$260000$...
        if not user.password.startswith("pbkdf2_"):
            print(f"  ⚠️ 发现明文密码: {user.password}")
            print("  🔧 准备修复...")

            # 询问是否修复
            response = input(
                f"  是否将用户 {user.email} 的密码重置为 '123456'? (y/n): "
            )

            if response.lower() == "y":
                user.set_password("123456")
                user.save()
                fixed_count += 1
                print("  ✅ 已重置密码为: 123456")
            else:
                print("  ⏭️ 跳过")
        else:
            normal_count += 1
            print("  ✓ 密码格式正常")

        print()

    print("=" * 60)
    print("📊 检查完成")
    print("=" * 60)
    print(f"✅ 密码正常的用户: {normal_count}")
    print(f"🔧 已修复的用户: {fixed_count}")
    print(f"📊 总计: {total_users}")

    if fixed_count > 0:
        print("\n⚠️ 重要提示:")
        print("1. 已修复用户的临时密码为: 123456")
        print("2. 请通知用户登录后立即修改密码")
        print("3. 建议在生产环境中强制用户首次登录后修改密码")


def create_test_user():
    """创建测试用户（正确方式）"""
    print("\n" + "=" * 60)
    print("➕ 创建测试用户")
    print("=" * 60)

    email = input("请输入邮箱 (默认: test@example.com): ") or "test@example.com"
    username = input("请输入用户名 (默认: testuser): ") or "testuser"
    password = input("请输入密码 (默认: 123456): ") or "123456"

    # 检查用户是否已存在
    if User.objects.filter(email=email).exists():
        print(f"❌ 邮箱 {email} 已被注册")
        return

    if User.objects.filter(username=username).exists():
        print(f"❌ 用户名 {username} 已被使用")
        return

    # 使用create_user方法创建用户（会自动加密密码）
    user = User.objects.create_user(email=email, username=username, password=password)

    print("\n✅ 用户创建成功!")
    print(f"  邮箱: {user.email}")
    print(f"  用户名: {user.username}")
    print(f"  密码: {password}")
    print(f"  密码是否加密: {'是' if user.password.startswith('pbkdf2_') else '否'}")


def main():
    print("\n🔧 Django用户管理工具")
    print("1. 检查并修复用户密码")
    print("2. 创建测试用户")
    print("3. 退出")

    choice = input("\n请选择操作 (1/2/3): ")

    if choice == "1":
        check_and_fix_passwords()
    elif choice == "2":
        create_test_user()
    elif choice == "3":
        print("👋 再见!")
        sys.exit(0)
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
