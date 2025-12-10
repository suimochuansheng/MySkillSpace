# permissions/permissions.py
from rest_framework import permissions


class HasPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 获取当前用户
        user = request.user

        # 如果是超级用户，直接通过
        if user.is_superuser:
            return True

        # 获取当前请求的URL
        path = request.path

        # 获取当前请求的权限标识
        # 这里需要根据你的URL设计来确定，例如：/api/users/ -> system:user:list
        # 一个简单示例：将URL转换为权限标识
        perms = f"system:{path.split('/')[2]}:{path.split('/')[3] if len(path.split('/')) > 3 else 'list'}"

        # 检查用户是否有该权限
        return user.has_perm(perms)
