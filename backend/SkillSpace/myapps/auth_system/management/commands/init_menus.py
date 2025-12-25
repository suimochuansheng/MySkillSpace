# auth_system/management/commands/init_menus.py
"""
初始化系统完整菜单数据（覆盖所有模块）
使用方法: python manage.py init_menus
"""
from auth_system.models import Menu
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "初始化系统完整菜单数据（覆盖所有模块）"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=" * 60))
        self.stdout.write(self.style.WARNING("开始初始化完整系统菜单..."))
        self.stdout.write(self.style.WARNING("=" * 60))

        # ========================================
        # 1. 工作台（一级菜单）
        # ========================================
        dashboard_menu, created = Menu.objects.get_or_create(
            name="工作台",
            defaults={
                "icon": "HomeFilled",
                "menu_type": "C",
                "path": "/dashboard",
                "component": "dashboard/HomePage",
                "perms": "dashboard:view",
                "order_num": 1,
                "remark": "工作台首页",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"创建菜单: {dashboard_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"  已存在: {dashboard_menu.name}"))

        # ========================================
        # 2. AI简历诊断（一级菜单）
        # ========================================
        resume_menu, created = Menu.objects.get_or_create(
            name="AI简历诊断",
            defaults={
                "icon": "Document",
                "menu_type": "C",
                "path": "/resume",
                "component": "resume/ResumePage",
                "perms": "resume:view",
                "order_num": 2,
                "remark": "AI简历分析与优化",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"创建菜单: {resume_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"  已存在: {resume_menu.name}"))

        # 简历管理按钮权限
        Menu.objects.get_or_create(
            name="上传简历",
            defaults={
                "parent": resume_menu,
                "menu_type": "F",
                "perms": "resume:upload",
                "order_num": 1,
            },
        )

        Menu.objects.get_or_create(
            name="分析简历",
            defaults={
                "parent": resume_menu,
                "menu_type": "F",
                "perms": "resume:analyze",
                "order_num": 2,
            },
        )

        Menu.objects.get_or_create(
            name="导出报告",
            defaults={
                "parent": resume_menu,
                "menu_type": "F",
                "perms": "resume:export",
                "order_num": 3,
            },
        )

        # ========================================
        # 3. 任务中心（一级菜单）
        # ========================================
        tasks_menu, created = Menu.objects.get_or_create(
            name="任务中心",
            defaults={
                "icon": "List",
                "menu_type": "C",
                "path": "/tasks",
                "component": "tasks/TasksPage",
                "perms": "tasks:view",
                "order_num": 3,
                "remark": "任务管理中心",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"创建菜单: {tasks_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"  已存在: {tasks_menu.name}"))

        # 任务管理按钮权限
        Menu.objects.get_or_create(
            name="新建任务",
            defaults={
                "parent": tasks_menu,
                "menu_type": "F",
                "perms": "tasks:add",
                "order_num": 1,
            },
        )

        Menu.objects.get_or_create(
            name="编辑任务",
            defaults={
                "parent": tasks_menu,
                "menu_type": "F",
                "perms": "tasks:edit",
                "order_num": 2,
            },
        )

        Menu.objects.get_or_create(
            name="删除任务",
            defaults={
                "parent": tasks_menu,
                "menu_type": "F",
                "perms": "tasks:delete",
                "order_num": 3,
            },
        )

        # ========================================
        # 4. 系统监控（一级菜单）
        # ========================================
        monitor_menu, created = Menu.objects.get_or_create(
            name="系统监控",
            defaults={
                "icon": "DataAnalysis",
                "menu_type": "C",
                "path": "/monitor",
                "component": "monitor/MonitorPage",
                "perms": "monitor:view",
                "order_num": 4,
                "remark": "系统性能监控",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"创建菜单: {monitor_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"  已存在: {monitor_menu.name}"))

        # ========================================
        # 5. AI助手（一级菜单）
        # ========================================
        ai_menu, created = Menu.objects.get_or_create(
            name="AI助手",
            defaults={
                "icon": "ChatDotRound",
                "menu_type": "C",
                "path": "/ai",
                "component": "ai/AiPage",
                "perms": "ai:view",
                "order_num": 5,
                "remark": "智能AI对话助手",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"创建菜单: {ai_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"  已存在: {ai_menu.name}"))

        # AI助手按钮权限
        Menu.objects.get_or_create(
            name="发送消息",
            defaults={
                "parent": ai_menu,
                "menu_type": "F",
                "perms": "ai:chat",
                "order_num": 1,
            },
        )

        Menu.objects.get_or_create(
            name="清除历史",
            defaults={
                "parent": ai_menu,
                "menu_type": "F",
                "perms": "ai:clear",
                "order_num": 2,
            },
        )

        # ========================================
        # 6. 系统管理（目录）
        # ========================================
        system_menu, created = Menu.objects.get_or_create(
            name="系统管理",
            defaults={
                "icon": "Setting",
                "menu_type": "M",
                "path": "/sys",
                "component": None,
                "perms": None,
                "order_num": 100,
                "remark": "系统管理目录",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"创建目录: {system_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"  已存在: {system_menu.name}"))

        # 6.1 用户管理
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
                "remark": "用户列表管理",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  创建菜单: {user_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"    已存在: {user_menu.name}"))

        # 用户管理按钮权限
        Menu.objects.get_or_create(
            name="用户新增",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:add",
                "order_num": 1,
            },
        )

        Menu.objects.get_or_create(
            name="用户编辑",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:edit",
                "order_num": 2,
            },
        )

        Menu.objects.get_or_create(
            name="用户删除",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:delete",
                "order_num": 3,
            },
        )

        Menu.objects.get_or_create(
            name="分配角色",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:assign",
                "order_num": 4,
            },
        )

        Menu.objects.get_or_create(
            name="重置密码",
            defaults={
                "parent": user_menu,
                "menu_type": "F",
                "perms": "system:user:resetPwd",
                "order_num": 5,
            },
        )

        # 6.2 角色管理
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
                "remark": "角色列表管理",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  创建菜单: {role_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"    已存在: {role_menu.name}"))

        # 角色管理按钮权限
        Menu.objects.get_or_create(
            name="角色新增",
            defaults={
                "parent": role_menu,
                "menu_type": "F",
                "perms": "system:role:add",
                "order_num": 1,
            },
        )

        Menu.objects.get_or_create(
            name="角色编辑",
            defaults={
                "parent": role_menu,
                "menu_type": "F",
                "perms": "system:role:edit",
                "order_num": 2,
            },
        )

        Menu.objects.get_or_create(
            name="角色删除",
            defaults={
                "parent": role_menu,
                "menu_type": "F",
                "perms": "system:role:delete",
                "order_num": 3,
            },
        )

        Menu.objects.get_or_create(
            name="分配权限",
            defaults={
                "parent": role_menu,
                "menu_type": "F",
                "perms": "system:role:assign",
                "order_num": 4,
            },
        )

        # 6.3 菜单管理
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
                "remark": "菜单列表管理",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  创建菜单: {menu_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"    已存在: {menu_menu.name}"))

        # 菜单管理按钮权限
        Menu.objects.get_or_create(
            name="菜单新增",
            defaults={
                "parent": menu_menu,
                "menu_type": "F",
                "perms": "system:menu:add",
                "order_num": 1,
            },
        )

        Menu.objects.get_or_create(
            name="菜单编辑",
            defaults={
                "parent": menu_menu,
                "menu_type": "F",
                "perms": "system:menu:edit",
                "order_num": 2,
            },
        )

        Menu.objects.get_or_create(
            name="菜单删除",
            defaults={
                "parent": menu_menu,
                "menu_type": "F",
                "perms": "system:menu:delete",
                "order_num": 3,
            },
        )

        # 6.4 操作日志
        operlog_menu, created = Menu.objects.get_or_create(
            name="操作日志",
            defaults={
                "parent": system_menu,
                "icon": "DocumentCopy",
                "menu_type": "C",
                "path": "/sys/operlog",
                "component": "sys/operationlog/index",
                "perms": "monitor:operlog:list",
                "order_num": 4,
                "remark": "操作日志查询",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  创建菜单: {operlog_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"    已存在: {operlog_menu.name}"))

        # 6.5 登录日志
        loginlog_menu, created = Menu.objects.get_or_create(
            name="登录日志",
            defaults={
                "parent": system_menu,
                "icon": "Document",
                "menu_type": "C",
                "path": "/sys/loginlog",
                "component": "sys/loginlog/index",
                "perms": "monitor:loginlog:list",
                "order_num": 5,
                "remark": "登录日志查询",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  创建菜单: {loginlog_menu.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"    已存在: {loginlog_menu.name}"))

        self.stdout.write(self.style.WARNING("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("系统完整菜单初始化完成！"))
        self.stdout.write(self.style.WARNING("=" * 60))
        self.stdout.write(self.style.NOTICE(f"菜单总数: {Menu.objects.count()}"))
        self.stdout.write(self.style.NOTICE("\n下一步操作:"))
        self.stdout.write(self.style.NOTICE("   1. 在角色管理中为角色分配菜单权限"))
        self.stdout.write(self.style.NOTICE("   2. 为用户分配角色"))
        self.stdout.write(self.style.NOTICE("   3. 登录测试权限控制"))
        self.stdout.write(self.style.WARNING("=" * 60 + "\n"))
