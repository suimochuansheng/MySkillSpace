from django.contrib import admin
from .models import User, Role, Menu

# 注册 Menu
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'menu_type', 'perms', 'order_num')
    list_filter = ('menu_type',)
    search_fields = ('name', 'perms')

# 注册 Role
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'create_time')
    filter_horizontal = ('menus',) # 方便多选菜单

# 注册 User (修改原来的 UserAdmin 以支持 roles)
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff')
    filter_horizontal = ('roles',) # 方便多选角色
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('个人信息', {'fields': ('username', 'avatar', 'phonenumber')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'roles')}), # 加上 roles
    )