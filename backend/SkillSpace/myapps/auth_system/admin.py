# auth_system/admin.py
"""
用户认证系统的Django Admin配置
在管理后台中管理用户账户
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    自定义用户管理界面
    支持通过邮箱搜索、过滤用户，查看详细信息
    """
    
    # 列表页显示的字段
    list_display = (
        'email',           # 邮箱
        'username',        # 用户名
        'is_active',       # 激活状态
        'is_staff',        # 管理员状态
        'date_joined',     # 注册时间
        'last_login',      # 最后登录时间
    )
    
    # 列表页右侧过滤器
    list_filter = (
        'is_active',       # 按激活状态过滤
        'is_staff',        # 按管理员状态过滤
        'is_superuser',    # 按超级用户状态过滤
        'date_joined',     # 按注册时间过滤
        'oauth_provider',  # 按登录方式过滤（普通/Google/GitHub）
    )
    
    # 搜索功能（支持邮箱、用户名搜索）
    search_fields = (
        'email',
        'username',
    )
    
    # 排序方式（默认按注册时间倒序）
    ordering = ('-date_joined',)
    
    # 只读字段（不可编辑）
    readonly_fields = (
        'date_joined',
        'last_login',
    )
    
    # 详情页字段分组
    fieldsets = (
        # 基本信息组
        ('基本信息', {
            'fields': ('email', 'username', 'password')
        }),
        
        # 权限信息组
        ('权限管理', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        
        # 时间信息组
        ('重要日期', {
            'fields': ('date_joined', 'last_login')
        }),
        
        # 第三方登录信息组
        ('第三方登录', {
            'fields': ('oauth_provider', 'oauth_id'),
            'classes': ('collapse',),  # 默认折叠
        }),
    )
    
    # 添加用户页面的字段
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
