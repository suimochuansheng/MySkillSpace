# auth_system/management/commands/assign_default_roles.py
"""
Django管理命令：为所有没有角色的用户分配默认角色
使用方法：python manage.py assign_default_roles
"""
from django.core.management.base import BaseCommand
from myapps.auth_system.models import Role, User


class Command(BaseCommand):
    help = "为所有没有角色的用户分配默认角色"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("自动分配用户默认角色"))
        self.stdout.write("=" * 60)
        self.stdout.write("")

        # 1. 检查系统角色
        roles = Role.objects.all()
        self.stdout.write(f"📋 系统中共有 {roles.count()} 个角色：")
        for role in roles:
            self.stdout.write(f"  - {role.name} ({role.code})")
        self.stdout.write("")

        if roles.count() == 0:
            self.stdout.write(self.style.ERROR("❌ 错误：系统中没有任何角色！"))
            self.stdout.write("   请先在Admin后台创建至少一个角色")
            return

        # 2. 找到默认角色
        default_role = Role.objects.filter(code="common").first()
        if not default_role:
            default_role = roles.first()

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ 将使用默认角色：{default_role.name} ({default_role.code})"
            )
        )
        self.stdout.write("")

        # 3. 查找没有角色的用户
        users_without_roles = []
        all_users = User.objects.all()

        for user in all_users:
            if user.roles.count() == 0:
                users_without_roles.append(user)

        self.stdout.write(f"🔍 找到 {len(users_without_roles)} 个没有角色的用户：")
        if len(users_without_roles) == 0:
            self.stdout.write("  （无）")
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("✅ 所有用户都已分配角色，无需修复"))
            return

        for user in users_without_roles:
            self.stdout.write(f"  - {user.email} ({user.username or '无用户名'})")
        self.stdout.write("")

        # 4. 执行修复
        self.stdout.write("🔧 开始修复...")
        fixed_count = 0

        for user in users_without_roles:
            try:
                user.roles.add(default_role)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  ✅ {user.email} - 已分配角色"))
                fixed_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ {user.email} - 失败：{e}"))

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ 修复完成！成功修复 {fixed_count}/{len(users_without_roles)} 个用户"
            )
        )
        self.stdout.write("=" * 60)
        self.stdout.write("")
        self.stdout.write("下一步：")
        self.stdout.write("  1. 这些用户现在可以正常登录了")
        self.stdout.write("  2. 如需修改用户角色，请访问Admin后台")
        self.stdout.write("  3. 未来新创建的用户会自动分配默认角色")
