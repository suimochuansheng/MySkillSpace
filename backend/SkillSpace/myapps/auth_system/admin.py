from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import LoginLog, Menu, OperationLog, Role, User


# 注册Menu
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "path", "menu_type", "perms", "order_num")
    list_filter = ("menu_type",)
    search_fields = ("name", "perms")


# 注册Role
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "create_time")
    filter_horizontal = ("menus",)  # 方便多选菜单


# ===========================================================
# 自定义用户创建和修改表单（确保密码加密）
# ===========================================================


class UserCreationForm(forms.ModelForm):
    """
    用户创建表单，包含密码和确认密码字段
    """

    password1 = forms.CharField(label="密码", widget=forms.PasswordInput, help_text="请输入密码，至少6位")
    password2 = forms.CharField(label="确认密码", widget=forms.PasswordInput, help_text="再次输入相同的密码")

    class Meta:
        model = User
        fields = ("email", "username", "avatar", "phonenumber")

    def clean_password2(self):
        """验证两次密码是否一致"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码输入不一致")
        return password2

    def save(self, commit=True):
        """保存用户，并使用set_password加密密码"""
        user = super().save(commit=False)
        password = self.cleaned_data["password1"]

        # 开发环境下保存明文密码（方便调试）
        if settings.DEBUG:
            user.plain_password = password

        user.set_password(password)  # ✅ 使用set_password加密
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    用户修改表单，密码字段为只读
    """

    password = ReadOnlyPasswordHashField(
        label="密码",
        help_text=("密码以加密形式存储，无法查看原始密码。 " '<a href="../password/">点击此处修改密码</a>。'),
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "plain_password",
            "avatar",
            "phonenumber",
            "is_active",
            "is_staff",
            "is_superuser",
            "roles",
        )

    def clean_password(self):
        """返回初始密码值，不允许直接修改"""
        return self.initial["password"]


# 注册User（使用自定义表单）
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    自定义用户Admin，确保密码正确加密
    """

    # 使用自定义表单
    form = UserChangeForm
    add_form = UserCreationForm

    # 列表页显示的字段
    list_display = (
        "email",
        "username",
        "plain_password_display",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "roles")

    # 搜索字段
    search_fields = ("email", "username")

    # 排序
    ordering = ("-date_joined",)

    # 编辑页面字段分组
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("个人信息", {"fields": ("username", "avatar", "phonenumber")}),
        (
            "开发调试",
            {
                "fields": ("plain_password",),
                "classes": ("collapse",),
                "description": "⚠️ 仅开发环境使用，生产环境请删除此字段！",
            },
        ),
        (
            "权限",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "roles"),
            },
        ),
        ("重要日期", {"fields": ("last_login", "date_joined")}),
    )

    # 添加用户页面字段分组
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
        (
            "个人信息",
            {
                "fields": ("avatar", "phonenumber"),
            },
        ),
        (
            "权限",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "roles"),
            },
        ),
    )

    # 多对多关系字段使用水平过滤器
    filter_horizontal = ("roles",)

    # 只读字段
    readonly_fields = ("last_login", "date_joined")

    def plain_password_display(self, obj):
        """显示明文密码（仅开发环境）"""
        if settings.DEBUG:
            return obj.plain_password or "（未设置）"
        else:
            return "⚠️ 生产环境已禁用"

    plain_password_display.short_description = "明文密码 (⚠️开发用)"


# 注册OperationLog（操作日志）
@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """操作日志Admin"""

    list_display = (
        "id",
        "username",
        "module",
        "action",
        "status",
        "ip_address",
        "created_at",
        "duration",
    )
    list_filter = ("action", "status", "module", "created_at")
    search_fields = ("username", "module", "description", "ip_address")
    readonly_fields = (
        "user",
        "username",
        "module",
        "action",
        "description",
        "method",
        "url",
        "ip_address",
        "user_agent",
        "request_params",
        "response_data",
        "status",
        "error_msg",
        "created_at",
        "duration",
    )
    ordering = ("-created_at",)

    # 只允许查看，不允许添加、修改、删除
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # 只允许超级用户删除日志
        return request.user.is_superuser

    fieldsets = (
        (
            "操作信息",
            {"fields": ("user", "username", "module", "action", "description")},
        ),
        (
            "请求信息",
            {"fields": ("method", "url", "ip_address", "user_agent", "request_params")},
        ),
        ("响应信息", {"fields": ("status", "response_data", "error_msg")}),
        ("时间信息", {"fields": ("created_at", "duration")}),
    )


# 注册LoginLog（登录日志）
@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    """登录日志Admin"""

    list_display = (
        "id",
        "username",
        "ip_address",
        "login_location",
        "browser",
        "os",
        "status",
        "msg",
        "login_time",
    )
    list_filter = ("status", "login_time")
    search_fields = ("username", "ip_address", "login_location")
    readonly_fields = (
        "username",
        "ip_address",
        "login_location",
        "browser",
        "os",
        "device",
        "status",
        "msg",
        "login_time",
    )
    ordering = ("-login_time",)

    # 只允许查看，不允许添加、修改、删除
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # 只允许超级用户删除日志
        return request.user.is_superuser

    fieldsets = (
        ("基本信息", {"fields": ("username", "ip_address", "login_location")}),
        ("设备信息", {"fields": ("browser", "os", "device")}),
        ("状态信息", {"fields": ("status", "msg", "login_time")}),
    )
