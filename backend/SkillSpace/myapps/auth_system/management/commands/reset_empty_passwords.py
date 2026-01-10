# auth_system/management/commands/reset_empty_passwords.py
"""
Django管理命令：批量重置空密码用户
使用方法：python manage.py reset_empty_passwords
"""
from django.core.management.base import BaseCommand

from auth_system.models import User


class Command(BaseCommand):
    help = "批量重置空密码用户（修复历史数据）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--default-password",
            type=str,
            default="ChangeMe123!",
            help="默认密码（用户需要首次登录后修改）",
        )

    def handle(self, *args, **options):
        default_password = options["default_password"]

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("批量重置空密码用户"))
        self.stdout.write("=" * 60)
        self.stdout.write("")

        # 1. 查找密码为空的用户
        users_with_empty_password = []
        all_users = User.objects.all()

        for user in all_users:
            # Django的密码是hash后的，以 pbkdf2_sha256$ 开头
            # 如果密码为空或不是正确格式，就是有问题的用户
            if not user.password or not user.password.startswith("pbkdf2_"):
                users_with_empty_password.append(user)

        self.stdout.write(f"🔍 找到 {len(users_with_empty_password)} 个密码异常的用户：")
        if len(users_with_empty_password) == 0:
            self.stdout.write("  （无）")
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("✅ 所有用户密码正常，无需修复"))
            return

        for user in users_with_empty_password:
            self.stdout.write(f"  - {user.email} ({user.username or '无用户名'})")
        self.stdout.write("")

        # 2. 询问确认
        self.stdout.write(f"将为这些用户设置默认密码：{default_password}")
        self.stdout.write("⚠️  请通知用户首次登录后立即修改密码！")
        self.stdout.write("")

        confirm = input("确认重置？(yes/no): ")
        if confirm.lower() != "yes":
            self.stdout.write(self.style.WARNING("已取消"))
            return

        # 3. 批量重置密码
        self.stdout.write("")
        self.stdout.write("🔧 开始重置...")
        fixed_count = 0

        for user in users_with_empty_password:
            try:
                user.set_password(default_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  ✅ {user.email} - 密码已重置"))
                fixed_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ {user.email} - 失败：{e}"))

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(f"✅ 修复完成！成功重置 {fixed_count}/{len(users_with_empty_password)} 个用户密码")
        )
        self.stdout.write("=" * 60)
        self.stdout.write("")
        self.stdout.write("下一步：")
        self.stdout.write(f"  1. 通知用户使用密码 '{default_password}' 登录")
        self.stdout.write("  2. 要求用户首次登录后立即修改密码")
        self.stdout.write("  3. 或者在Admin后台为每个用户单独重置密码")
