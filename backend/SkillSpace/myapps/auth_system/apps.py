# auth_system/apps.py
"""
用户认证系统应用配置
提供用户登录、注册、登出等认证功能
"""
from django.apps import AppConfig


class AuthSystemConfig(AppConfig):
    """认证系统应用配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_system'
    verbose_name = '用户认证系统'
