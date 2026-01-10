"""
自定义权限类 - 基于RBAC菜单权限
"""

from rest_framework import permissions

# ==========================================
# 工具函数：检查用户权限
# ==========================================


def has_permission(user, perm_code):
    """
    检查用户是否拥有指定权限标识

    Args:
        user: User对象
        perm_code: 权限标识，如 "system:user:list"

    Returns:
        bool: 是否有权限
    """
    # 1. 超级用户拥有所有权限
    if user.is_superuser:
        return True

    # 2. 未登录用户无权限
    if not user.is_authenticated:
        return False

    # 3. 从数据库导入模型（延迟导入避免循环依赖）
    from .models import Menu

    # 4. 获取用户的所有角色
    user_roles = user.roles.all()

    if not user_roles.exists():
        return False

    # 5. 查询角色关联的菜单中是否包含该权限标识
    has_perm = Menu.objects.filter(role__in=user_roles, perms=perm_code).exists()  # 用户拥有的角色  # 匹配权限标识

    return has_perm


def get_user_permissions(user):
    """
    获取用户的所有权限标识列表

    Args:
        user: User对象

    Returns:
        set: 权限标识集合，如 {"system:user:list", "system:user:add"}
    """
    # 超级用户返回空集合（因为超级用户拥有所有权限，无需检查）
    if user.is_superuser:
        return set()

    if not user.is_authenticated:
        return set()

    from .models import Menu

    # 获取用户的所有角色
    user_roles = user.roles.all()

    # 获取角色关联的菜单权限
    menus = Menu.objects.filter(role__in=user_roles).distinct()

    # 提取权限标识
    perms = set()
    for menu in menus:
        if menu.perms:
            perms.add(menu.perms)

    return perms


# ==========================================
# DRF权限类
# ==========================================


class MenuPermission(permissions.BasePermission):
    """
    基于菜单权限的DRF权限类

    用法：
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [MenuPermission]
            permission_required = 'system:user:list'  # 需要的权限标识

    或者在action中指定：
        @action(detail=True, methods=['post'])
        def custom_action(self, request, pk=None):
            self.permission_required = 'system:user:custom'
            ...
    """

    def has_permission(self, request, view):
        """
        检查用户是否有视图所需的权限
        """
        # 1. 检查用户是否登录
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. 超级用户拥有所有权限
        if request.user.is_superuser:
            return True

        # 3. 获取视图要求的权限标识
        perm_code = getattr(view, "permission_required", None)

        # 4. 如果视图没有指定权限，默认只检查登录
        if not perm_code:
            return True

        # 5. 检查权限
        return has_permission(request.user, perm_code)


class ActionPermission(permissions.BasePermission):
    """
    基于不同HTTP方法的权限类

    用法：
        class UserViewSet(viewsets.ModelViewSet):
            permission_classes = [ActionPermission]
            permission_map = {
                'list': 'system:user:list',
                'retrieve': 'system:user:query',
                'create': 'system:user:add',
                'update': 'system:user:edit',
                'partial_update': 'system:user:edit',
                'destroy': 'system:user:delete',
            }
    """

    def has_permission(self, request, view):
        """
        根据action检查对应的权限
        """
        # 1. 检查用户是否登录
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. 超级用户拥有所有权限
        if request.user.is_superuser:
            return True

        # 3. 获取权限映射表
        permission_map = getattr(view, "permission_map", None)

        if not permission_map:
            # 如果没有定义权限映射，默认只检查登录
            return True

        # 4. 获取当前action
        action = getattr(view, "action", None)

        if not action:
            # 如果无法获取action，尝试从basename推断
            action = view.basename if hasattr(view, "basename") else None

        # 5. 获取该action需要的权限
        perm_code = permission_map.get(action, None)

        if not perm_code:
            # 如果该action没有定义权限，默认允许
            return True

        # 6. 检查权限
        return has_permission(request.user, perm_code)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    对象级权限：只有对象拥有者或管理员可以操作

    用法：
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    """

    def has_object_permission(self, request, view, obj):
        """
        检查用户是否是对象的拥有者或管理员
        """
        # 超级用户或staff可以操作任何对象
        if request.user.is_superuser or request.user.is_staff:
            return True

        # 检查对象是否有owner/user/created_by字段
        owner_fields = ["owner", "user", "created_by"]

        for field in owner_fields:
            if hasattr(obj, field):
                owner = getattr(obj, field)
                if owner == request.user:
                    return True

        return False


class IsAdminUser(permissions.BasePermission):
    """
    只有管理员可以访问

    用法：
        class AdminOnlyViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAdminUser]
    """

    def has_permission(self, request, view):
        """
        检查用户是否是管理员
        """
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


# ==========================================
# 权限装饰器（用于函数视图）
# ==========================================

from functools import wraps

from rest_framework import status as http_status
from rest_framework.response import Response


def permission_required(perm_code):
    """
    权限装饰器 - 用于函数视图或ViewSet的action

    用法：
        @permission_required('system:user:delete')
        @action(detail=True, methods=['post'])
        def delete_user(self, request, pk=None):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request_or_self, *args, **kwargs):
            # 兼容类视图和函数视图
            if hasattr(request_or_self, "request"):
                # ViewSet的action，request_or_self是self
                request = request_or_self.request
            else:
                # 函数视图，request_or_self是request
                request = request_or_self

            # 检查权限
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "身份验证失败，请先登录"},
                    status=http_status.HTTP_401_UNAUTHORIZED,
                )

            if not has_permission(request.user, perm_code):
                return Response(
                    {"detail": f"您没有执行该操作的权限（需要权限：{perm_code}）"},
                    status=http_status.HTTP_403_FORBIDDEN,
                )

            return view_func(request_or_self, *args, **kwargs)

        return wrapped_view

    return decorator
