"""
SkillSpace 系统初始化脚本
用于首次部署时初始化数据库、创建超级管理员、初始化菜单和角色

使用方法:
    cd /path/to/skillspace/backend/scripts
    python init_system.py

功能:
    1. 运行数据库迁移
    2. 初始化菜单数据
    3. 创建默认角色（系统管理员、普通用户）
    4. 创建超级管理员账号
    5. 为角色分配菜单权限
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

from auth_system.models import Menu, Role
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def run_migrations():
    """运行数据库迁移"""
    print_section("步骤1: 运行数据库迁移")
    try:
        call_command("makemigrations")
        call_command("migrate")
        print("✅ 数据库迁移完成")
        return True
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False


def init_menus():
    """初始化菜单数据"""
    print_section("步骤2: 初始化菜单数据")
    try:
        call_command("init_menus")
        menu_count = Menu.objects.count()
        print(f"✅ 菜单初始化完成，共 {menu_count} 个菜单")
        return True
    except Exception as e:
        print(f"❌ 菜单初始化失败: {e}")
        return False


def create_default_roles():
    """创建默认角色"""
    print_section("步骤3: 创建默认角色")

    try:
        # 创建系统管理员角色
        admin_role, created = Role.objects.get_or_create(
            code="admin",
            defaults={
                "name": "系统管理员",
                "remark": "系统管理员，拥有所有权限",
            },
        )

        if created:
            print(f"✅ 创建角色: {admin_role.name}")
            # 分配所有菜单
            all_menus = Menu.objects.all()
            admin_role.menus.set(all_menus)
            print(f"   已分配 {all_menus.count()} 个菜单权限")
        else:
            print(f"ℹ️  角色已存在: {admin_role.name}")
            # 确保拥有所有菜单
            all_menus = Menu.objects.all()
            admin_role.menus.set(all_menus)
            print(f"   已更新菜单权限: {all_menus.count()} 个")

        # 创建普通用户角色
        normal_role, created = Role.objects.get_or_create(
            code="normal",
            defaults={
                "name": "普通用户",
                "remark": "普通用户，只有基础功能权限",
            },
        )

        if created:
            print(f"✅ 创建角色: {normal_role.name}")
            # 分配基础菜单（工作台、AI简历、AI助手）
            basic_menus = Menu.objects.filter(
                name__in=["工作台", "AI简历诊断", "AI助手"]
            )
            normal_role.menus.set(basic_menus)
            print(f"   已分配 {basic_menus.count()} 个基础菜单")
        else:
            print(f"ℹ️  角色已存在: {normal_role.name}")

        return True, admin_role

    except Exception as e:
        print(f"❌ 角色创建失败: {e}")
        return False, None


def create_superuser(admin_role):
    """创建超级管理员账号"""
    print_section("步骤4: 创建超级管理员账号")

    # 默认管理员信息
    default_email = "admin@skillspace.com"
    default_username = "admin"
    default_password = "Admin@123456"

    # 检查是否已存在
    if User.objects.filter(email=default_email).exists():
        print(f"ℹ️  管理员账号已存在: {default_email}")
        user = User.objects.get(email=default_email)
    else:
        print("\n创建超级管理员账号:")
        print(f"  邮箱: {default_email}")
        print(f"  用户名: {default_username}")
        print(f"  密码: {default_password}")

        confirm = (
            input("\n是否使用以上默认配置创建? (y/n，回车默认y): ").strip().lower()
        )

        if confirm in ["", "y", "yes"]:
            email = default_email
            username = default_username
            password = default_password
        else:
            email = input("请输入邮箱: ").strip() or default_email
            username = input("请输入用户名: ").strip() or default_username
            password = input("请输入密码: ").strip() or default_password

        try:
            # 创建超级用户
            user = User.objects.create_superuser(
                email=email, username=username, password=password
            )
            print("✅ 超级管理员创建成功")
            print(f"   邮箱: {user.email}")
            print(f"   用户名: {user.username}")
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            return False

    # 分配系统管理员角色
    if admin_role:
        user.roles.add(admin_role)
        print(f"✅ 已分配角色: {admin_role.name}")

    return True


def print_summary():
    """打印初始化总结"""
    print_section("初始化完成总结")

    # 统计信息
    menu_count = Menu.objects.count()
    role_count = Role.objects.count()
    user_count = User.objects.count()

    print("\n📊 系统数据统计:")
    print(f"  菜单总数: {menu_count}")
    print(f"  角色总数: {role_count}")
    print(f"  用户总数: {user_count}")

    # 角色详情
    print("\n👥 角色列表:")
    for role in Role.objects.all():
        print(f"  - {role.name} ({role.code}): {role.menus.count()} 个菜单权限")

    # 管理员信息
    print("\n🔑 管理员账号:")
    admin_users = User.objects.filter(is_superuser=True)
    for user in admin_users:
        print(f"  - {user.email} ({user.username})")
        roles = user.roles.all()
        if roles:
            print(f"    角色: {', '.join([r.name for r in roles])}")

    print("\n✅ 系统初始化完成！")
    print("\n🚀 下一步:")
    print("  1. 启动Django服务器: python manage.py runserver")
    print("  2. 访问前端页面并登录管理员账号")
    print("  3. 在角色管理中可以调整角色权限")
    print("  4. 在用户管理中可以创建更多用户")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "SkillSpace 系统初始化" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")

    # 步骤1: 数据库迁移
    if not run_migrations():
        print("\n❌ 初始化失败：数据库迁移出错")
        return

    # 步骤2: 初始化菜单
    if not init_menus():
        print("\n❌ 初始化失败：菜单初始化出错")
        return

    # 步骤3: 创建默认角色
    success, admin_role = create_default_roles()
    if not success:
        print("\n❌ 初始化失败：角色创建出错")
        return

    # 步骤4: 创建超级管理员
    if not create_superuser(admin_role):
        print("\n❌ 初始化失败：管理员创建出错")
        return

    # 打印总结
    print_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  初始化已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
