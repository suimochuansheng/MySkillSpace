# auth_system/serializers.py
from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import LoginLog, Menu, OperationLog, Role, User

# ==========================================
# 新增/修改：RBAC 权限相关序列化器
# ==========================================


class MenuSerializer(serializers.ModelSerializer):
    """
    菜单序列化器，支持递归显示子菜单
    """

    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = "__all__"

    def get_children(self, obj):
        # 递归获取子菜单 (children_list 会在 View 中预处理好)
        if hasattr(obj, "children_list"):
            return MenuSerializer(obj.children_list, many=True).data
        return []


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化器
    """

    menus = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Role
        fields = "__all__"

    def get_menus(self, obj):
        # 返回菜单ID列表，用于前端选中状态
        return [menu.id for menu in obj.menus.all()]


# ==========================================
# 修改：用户相关序列化器
# ==========================================


class UserSerializer(serializers.ModelSerializer):
    """
    用户基础信息序列化器 (增加角色信息返回)
    """

    roles = serializers.SerializerMethodField()
    role_ids = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",  # 添加password字段（write_only）
            "avatar",
            "phonenumber",
            "date_joined",
            "last_login",
            "roles",
            "role_ids",
            "is_active",
            "is_superuser",  # 添加超级管理员标识
        ]
        read_only_fields = ["id", "date_joined", "last_login"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def get_roles(self, obj):
        # 返回用户拥有的角色名称列表，如 "admin,common"
        return ",".join([role.name for role in obj.roles.all()])

    def get_role_ids(self, obj):
        # 返回角色ID列表，用于前端角色分配
        return [role.id for role in obj.roles.all()]

    def create(self, validated_data):
        """管理员创建用户时，正确处理密码hash"""
        password = validated_data.pop("password", None)
        user = User.objects.create(**validated_data)

        # 如果提供了密码，进行hash
        if password:
            user.set_password(password)
            user.save()

        return user

    def update(self, instance, validated_data):
        """更新用户时，正确处理密码hash"""
        password = validated_data.pop("password", None)

        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 如果提供了密码，进行hash
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器 (保持原逻辑)
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={"input_type": "password"},
        help_text="密码至少6位",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="再次输入密码以确认",
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "password_confirm"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("该邮箱已被注册，请使用其他邮箱")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "两次输入的密码不一致"}
            )
        attrs.pop("password_confirm")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            username=validated_data.get("username", ""),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器 (增强验证逻辑)
    """

    account = serializers.CharField(
        required=True, help_text="登录账户（邮箱地址或用户名）"
    )
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    user = UserSerializer(read_only=True)

    def validate(self, attrs):
        account = attrs.get("account")
        password = attrs.get("password")
        user_obj = None

        # 1. 查找用户
        if "@" in account:
            try:
                user_obj = User.objects.get(email=account)
            except User.DoesNotExist:
                pass
        else:
            try:
                user_obj = User.objects.get(username=account)
            except User.DoesNotExist:
                pass

        # 2. 验证密码
        if user_obj:
            # authenticate 需要 username 参数，这里传入 email (因为 MODEL 配置了 USERNAME_FIELD='email')
            user = authenticate(
                request=self.context.get("request"),
                username=user_obj.email,
                password=password,
            )
        else:
            user = None

        if not user:
            raise serializers.ValidationError({"detail": "账户或密码错误，请重试"})

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "该账户已被禁用，请联系管理员"}
            )

        attrs["user"] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """
    修改密码序列化器 (保持原逻辑)
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("当前密码错误")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "两次输入的新密码不一致"}
            )
        attrs.pop("new_password_confirm")
        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


# ==========================================
# 日志相关序列化器
# ==========================================


class OperationLogSerializer(serializers.ModelSerializer):
    """
    操作日志序列化器
    """

    status_display = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()

    class Meta:
        model = OperationLog
        fields = [
            "id",
            "username",
            "module",
            "action",
            "action_display",
            "description",
            "method",
            "url",
            "ip_address",
            "user_agent",
            "status",
            "status_display",
            "error_msg",
            "created_at",
            "duration",
        ]
        read_only_fields = fields

    def get_status_display(self, obj):
        return "成功" if obj.status == "0" else "失败"

    def get_action_display(self, obj):
        return obj.get_action_display()


class LoginLogSerializer(serializers.ModelSerializer):
    """
    登录日志序列化器
    """

    status_display = serializers.SerializerMethodField()

    class Meta:
        model = LoginLog
        fields = [
            "id",
            "username",
            "ip_address",
            "login_location",
            "browser",
            "os",
            "device",
            "status",
            "status_display",
            "msg",
            "login_time",
        ]
        read_only_fields = fields

    def get_status_display(self, obj):
        return "成功" if obj.status == "0" else "失败"
