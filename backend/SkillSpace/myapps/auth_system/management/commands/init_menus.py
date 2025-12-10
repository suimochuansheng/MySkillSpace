# auth_system/management/commands/init_menus.py
"""
初始化系统菜单的Django管理命令
使用方法: python manage.py init_menus
"""
from django.core.management.base import BaseCommand
from auth_system.models import Menu


class Command(BaseCommand):
    help = "初始化系统默认菜单数据"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("开始初始化系统菜单..."))

        # 清空现有菜单（可选，谨慎使用）
        # Menu.objects.all().delete()

        # 创建系统管理目录（一级菜单）
        system_menu, created = Menu.objects.get_or_create(
            name="系统管理",
            defaults={
                "icon": "Setting",
                "menu_type": "M",
                "path": "/sys",
                "component": None,
                "perms": None,
                "order_num": 1,
                "remark": "系统管理目录，包含用户、角色、菜单管理",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ 创建菜单: {system_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"  已存在: {system_menu.name}"))

        # 创建用户管理（二级菜单）
        user_menu, created = Menu.objects.get_or_create(
            name="用户管理",
            defaults={
                "parent": system_menu,
                "icon": "User",
                "menu_type": "C",
                "path": "/sys/user",
                "component": "sys/user/index",
                "perms": "system:user:list",
                "order_num": 1,
                "remark": "用户列表管理页面",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✓ 创建菜单: {user_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"    已存在: {user_menu.name}"))

        # 创建角色管理（二级菜单）
        role_menu, created = Menu.objects.get_or_create(
            name="角色管理",
            defaults={
                "parent": system_menu,
                "icon": "Avatar",
                "menu_type": "C",
                "path": "/sys/role",
                "component": "sys/role/index",
                "perms": "system:role:list",
                "order_num": 2,
                "remark": "角色列表管理页面",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✓ 创建菜单: {role_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"    已存在: {role_menu.name}"))

        # 创建菜单管理（二级菜单）
        menu_menu, created = Menu.objects.get_or_create(
            name="菜单管理",
            defaults={
                "parent": system_menu,
                "icon": "Menu",
                "menu_type": "C",
                "path": "/sys/menu",
                "component": "sys/menu/index",
                "perms": "system:menu:list",
                "order_num": 3,
                "remark": "菜单列表管理页面",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✓ 创建菜单: {menu_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"    已存在: {menu_menu.name}"))

        # 创建用户管理的按钮权限
        user_add_btn, _ = Menu.objects.get_or_create(
            name="用户新增",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:add",
                "order_num": 1,
            },
        )

        user_edit_btn, _ = Menu.objects.get_or_create(
            name="用户编辑",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:edit",
                "order_num": 2,
            },
        )

        user_delete_btn, _ = Menu.objects.get_or_create(
            name="用户删除",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:delete",
                "order_num": 3,
            },
        )

        user_assign_btn, _ = Menu.objects.get_or_create(
            name="分配角色",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:assign",
                "order_num": 4,
            },
        )

        self.stdout.write(self.style.SUCCESS("\n系统菜单初始化完成！"))
        self.stdout.write(self.style.NOTICE(f"菜单总数: {Menu.objects.count()}"))
        self.stdout.write(self.style.NOTICE("提示: 请在角色管理中为角色分配菜单权限"))
