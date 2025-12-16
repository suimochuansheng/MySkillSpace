# auth_system/views.py
from django.contrib.auth import login, logout
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Menu, Role, User, OperationLog, LoginLog
from .permissions import ActionPermission, permission_required
from .log_utils import record_login_log
from .serializers import (
    MenuSerializer,
    PasswordChangeSerializer,
    RoleSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    OperationLogSerializer,
    LoginLogSerializer,
)


# ==========================================
# 工具函数：构建菜单树
# ==========================================
def build_menu_tree(menu_queryset):
    """
    将扁平的菜单QuerySet转换为树形结构
    """
    menu_list = list(menu_queryset)
    menu_dict = {menu.id: menu for menu in menu_list}
    roots = []

    for menu in menu_list:
        menu.children_list = []  # 初始化临时属性
        parent_id = menu.parent_id
        if parent_id and parent_id in menu_dict:
            parent_menu = menu_dict[parent_id]
            parent_menu.children_list.append(menu)
        else:
            roots.append(menu)
    return roots


# ==========================================
# 视图类
# ==========================================


class UserRegistrationView(generics.CreateAPIView):
    """
    用户注册API (保留原功能)
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "注册成功，欢迎加入 Skillspace！",
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    """
    用户登录API (升级：返回Token、用户信息、动态路由菜单、权限标识)
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )

        # 验证失败记录日志
        if not serializer.is_valid():
            account = request.data.get('account', '未知账号')
            record_login_log(
                request,
                username=account,
                status='1',
                msg='账户或密码错误'
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # 1. 建立 Session
        login(request, user)

        # 2. 获取权限和菜单
        roles = user.roles.all()
        # 获取角色关联的菜单，去重并排序
        menus = Menu.objects.filter(role__in=roles).distinct().order_by("order_num")

        # 3. 构建菜单树 (用于左侧导航栏)
        # 过滤掉类型为 'F' (按钮) 的，只保留目录 'M' 和 菜单 'C'，如果前端需要全部则去掉 filter
        menu_tree = build_menu_tree(menus.exclude(menu_type="F"))

        # 4. 获取按钮权限标识 (用于页面按钮显隐)
        perms = set()
        for menu in menus:
            if menu.perms:
                perms.add(menu.perms)

        # 5. 记录登录成功日志
        record_login_log(
            request,
            username=user.email,
            status='0',
            msg='登录成功'
        )

        # 6. 返回完整数据
        return Response(
            {
                "code": 200,
                "message": "登录成功！🎉 欢迎回到 Skillspace！",
                "token": request.session.session_key
                or "session_active",  # Session模式下Token非必须，但前端可能需要一个非空值
                "user": UserSerializer(user).data,
                "menuList": MenuSerializer(menu_tree, many=True).data,
                "authorities": list(perms),
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutView(APIView):
    """
    用户登出API
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "登出成功"}, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    获取当前用户信息API
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetRoutersView(APIView):
    """
    获取动态路由API (用于前端刷新页面后重新获取菜单)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        roles = user.roles.all()
        menus = Menu.objects.filter(role__in=roles).distinct().order_by("order_num")
        # 构建树，通常路由只需 M 和 C 类型
        menu_tree = build_menu_tree(menus.exclude(menu_type="F"))

        # 获取按钮权限标识 (用于页面按钮显隐)
        perms = set()
        for menu in menus:
            if menu.perms:
                perms.add(menu.perms)

        return Response(
            {
                "code": 200,
                "menuList": MenuSerializer(menu_tree, many=True).data,
                "authorities": list(perms),  # 添加权限标识数组
            }
        )


class PasswordChangeView(APIView):
    """
    修改密码API
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logout(request)
        return Response(
            {"message": "密码修改成功，请使用新密码重新登录"}, status=status.HTTP_200_OK
        )


class CheckEmailView(APIView):
    """
    检查邮箱是否存在API
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "")
        if not email:
            return Response(
                {"available": False, "message": "请输入邮箱"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        exists = User.objects.filter(email__iexact=email).exists()
        return Response(
            {
                "available": not exists,
                "message": "该邮箱已被注册" if exists else "该邮箱可以使用",
            },
            status=status.HTTP_200_OK,
        )


# ==========================================
# ViewSet：权限管理CRUD接口
# ==========================================


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    用户管理ViewSet - 提供完整的CRUD接口
    GET /api/auth/users/ - 获取用户列表
    POST /api/auth/users/ - 创建用户
    GET /api/auth/users/{id}/ - 获取用户详情
    PUT /api/auth/users/{id}/ - 更新用户
    DELETE /api/auth/users/{id}/ - 删除用户
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [ActionPermission]

    # 权限映射：定义每个action需要的权限
    permission_map = {
        'list': 'system:user:list',        # 查看用户列表
        'retrieve': 'system:user:query',   # 查看用户详情
        'create': 'system:user:add',       # 新增用户
        'update': 'system:user:edit',      # 编辑用户
        'partial_update': 'system:user:edit',  # 部分更新用户
        'destroy': 'system:user:delete',   # 删除用户
        'reset_password': 'system:user:resetPwd',  # 重置密码
        'assign_roles': 'system:user:assign',      # 分配角色
    }

    def get_queryset(self):
        # 可以根据需要添加过滤逻辑
        return User.objects.all().order_by("-date_joined")

    @action(detail=True, methods=["post"])
    @permission_required('system:user:resetPwd')
    def reset_password(self, request, pk=None):
        """重置用户密码（仅管理员）"""
        user = self.get_object()
        new_password = request.data.get("new_password")

        # 验证新密码
        if not new_password or len(new_password) < 6:
            return Response(
                {"detail": "密码至少需要6位字符"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response({"message": f"用户 {user.username} 的密码已重置"})

    @action(detail=True, methods=["post"])
    @permission_required('system:user:assign')
    def assign_roles(self, request, pk=None):
        """为用户分配角色（仅管理员）"""
        user = self.get_object()
        role_ids = request.data.get("role_ids", [])
        roles = Role.objects.filter(id__in=role_ids)
        user.roles.set(roles)
        return Response({"message": "角色分配成功", "user": UserSerializer(user).data})


class RoleManagementViewSet(viewsets.ModelViewSet):
    """
    角色管理ViewSet - 提供完整的CRUD接口
    GET /api/auth/roles/ - 获取角色列表
    POST /api/auth/roles/ - 创建角色
    GET /api/auth/roles/{id}/ - 获取角色详情
    PUT /api/auth/roles/{id}/ - 更新角色
    DELETE /api/auth/roles/{id}/ - 删除角色
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [ActionPermission]

    # 权限映射：定义每个action需要的权限
    permission_map = {
        'list': 'system:role:list',        # 查看角色列表
        'retrieve': 'system:role:query',   # 查看角色详情
        'create': 'system:role:add',       # 新增角色
        'update': 'system:role:edit',      # 编辑角色
        'partial_update': 'system:role:edit',  # 部分更新角色
        'destroy': 'system:role:delete',   # 删除角色
        'assign_menus': 'system:role:assign',  # 分配菜单权限
    }

    @action(detail=True, methods=["post"])
    @permission_required('system:role:assign')
    def assign_menus(self, request, pk=None):
        """为角色分配菜单权限（仅管理员）"""
        role = self.get_object()
        menu_ids = request.data.get("menu_ids", [])
        menus = Menu.objects.filter(id__in=menu_ids)
        role.menus.set(menus)
        return Response(
            {"message": "菜单权限分配成功", "role": RoleSerializer(role).data}
        )


class MenuManagementViewSet(viewsets.ModelViewSet):
    """
    菜单管理ViewSet - 提供完整的CRUD接口
    GET /api/auth/menus/ - 获取菜单列表
    POST /api/auth/menus/ - 创建菜单
    GET /api/auth/menus/{id}/ - 获取菜单详情
    PUT /api/auth/menus/{id}/ - 更新菜单
    DELETE /api/auth/menus/{id}/ - 删除菜单
    """

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [ActionPermission]

    # 权限映射：定义每个action需要的权限
    permission_map = {
        'list': 'system:menu:list',        # 查看菜单列表
        'retrieve': 'system:menu:query',   # 查看菜单详情
        'create': 'system:menu:add',       # 新增菜单
        'update': 'system:menu:edit',      # 编辑菜单
        'partial_update': 'system:menu:edit',  # 部分更新菜单
        'destroy': 'system:menu:delete',   # 删除菜单
        'tree': 'system:menu:list',        # 获取菜单树
    }

    # 系统核心菜单名称，不允许删除
    PROTECTED_MENUS = ["系统管理", "用户管理", "角色管理", "菜单管理"]

    def get_queryset(self):
        # 按照order_num排序
        return Menu.objects.all().order_by("order_num")

    def destroy(self, request, *args, **kwargs):
        """重写删除方法，防止删除核心菜单"""
        instance = self.get_object()

        # 检查是否为保护的核心菜单
        if instance.name in self.PROTECTED_MENUS:
            return Response(
                {"detail": f"「{instance.name}」是系统核心功能，不允许删除"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查是否有子菜单
        if instance.children.exists():
            return Response(
                {"detail": f"「{instance.name}」下还有子菜单，请先删除子菜单"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 执行删除
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """获取菜单树结构"""
        menus = Menu.objects.all().order_by("order_num")
        menu_tree = build_menu_tree(menus)
        return Response(MenuSerializer(menu_tree, many=True).data)


# ==========================================
# 日志管理ViewSet
# ==========================================


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    操作日志管理ViewSet（只读）
    提供操作日志的查询和筛选功能
    """

    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [ActionPermission]
    pagination_class = PageNumberPagination

    # 权限映射
    permission_map = {
        "list": "monitor:operlog:list",
        "retrieve": "monitor:operlog:query",
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        # 筛选条件
        username = self.request.query_params.get("username")
        module = self.request.query_params.get("module")
        action = self.request.query_params.get("action")
        status_param = self.request.query_params.get("status")

        if username:
            queryset = queryset.filter(username__icontains=username)
        if module:
            queryset = queryset.filter(module__icontains=module)
        if action:
            queryset = queryset.filter(action=action)
        if status_param is not None:
            queryset = queryset.filter(status=status_param)

        return queryset.order_by("-created_at")


class LoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    登录日志管理ViewSet（只读）
    提供登录日志的查询和筛选功能
    """

    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    permission_classes = [ActionPermission]
    pagination_class = PageNumberPagination

    # 权限映射
    permission_map = {
        "list": "monitor:loginlog:list",
        "retrieve": "monitor:loginlog:query",
    }

    def get_queryset(self):
        queryset = super().get_queryset()

        # 筛选条件
        username = self.request.query_params.get("username")
        ip_address = self.request.query_params.get("ip_address")
        status_param = self.request.query_params.get("status")

        if username:
            queryset = queryset.filter(username__icontains=username)
        if ip_address:
            queryset = queryset.filter(ip_address__icontains=ip_address)
        if status_param is not None:
            queryset = queryset.filter(status=status_param)

        return queryset.order_by("-login_time")

