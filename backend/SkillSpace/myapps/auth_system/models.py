from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("用户必须提供邮箱地址")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        # 开发环境下保存明文密码（方便调试）
        if settings.DEBUG and password:
            user.plain_password = password

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# 1. 新增：菜单/权限模型 (对应PDF中的 SysMenu)
class Menu(models.Model):
    """
    系统菜单/权限表
    对应前端的路由和按钮权限
    """

    MENU_TYPE_CHOICES = (
        ("M", "目录"),  # Directory
        ("C", "菜单"),  # Menu
        ("F", "按钮"),  # Button/Function
    )

    name = models.CharField("菜单名称", max_length=50)
    icon = models.CharField("菜单图标", max_length=100, null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="上级菜单",
        related_name="children",
    )
    order_num = models.IntegerField("显示顺序", default=0)
    path = models.CharField("路由地址", max_length=200, null=True, blank=True)
    component = models.CharField("组件路径", max_length=255, null=True, blank=True)
    menu_type = models.CharField(
        "菜单类型", max_length=1, choices=MENU_TYPE_CHOICES, default="C"
    )
    perms = models.CharField(
        "权限标识",
        max_length=100,
        null=True,
        blank=True,
        help_text="如 system:user:list",
    )
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    remark = models.CharField("备注", max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "系统菜单"
        verbose_name_plural = verbose_name
        # 按显示顺序升序排列，顺序越小越靠前
        ordering = ["order_num"]
        db_table = "sys_menu"

    def __str__(self):
        return self.name


# 2. 新增：角色模型 (对应PDF中的 SysRole)
class Role(models.Model):
    """
    系统角色表
    """

    name = models.CharField("角色名称", max_length=30, unique=True)
    code = models.CharField(
        "角色权限字符", max_length=100, unique=True, help_text="如 admin, common"
    )
    remark = models.CharField("备注", max_length=500, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    # 角色与菜单是多对多关系
    menus = models.ManyToManyField(
        Menu, verbose_name="拥有菜单", blank=True, db_table="sys_role_menu"
    )

    class Meta:
        verbose_name = "系统角色"
        verbose_name_plural = verbose_name
        db_table = "sys_role"

    def __str__(self):
        return self.name


# 3. 修改：用户模型 (关联角色)
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("邮箱地址", max_length=255, unique=True, db_index=True)
    username = models.CharField("用户名", max_length=150, blank=True, null=True)
    avatar = models.CharField(
        "头像", max_length=255, default="default.jpg", null=True, blank=True
    )  # PDF中提到的头像
    phonenumber = models.CharField("手机号码", max_length=11, null=True, blank=True)

    # 开发环境专用：明文密码字段（仅用于调试，生产环境应删除）
    plain_password = models.CharField(
        "明文密码",
        max_length=128,
        blank=True,
        null=True,
        help_text="⚠️ 仅开发环境使用，用于调试。生产环境请删除此字段！"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # 用户与角色是多对多关系
    roles = models.ManyToManyField(
        Role, verbose_name="拥有角色", blank=True, db_table="sys_user_role"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户列表"
        db_table = "sys_user"  # 修改表名以匹配PDF习惯
        # 按注册时间降序排列，最新注册的用户在前
        ordering = ["-date_joined"]


# 4. 新增：操作日志模型
class OperationLog(models.Model):
    """
    操作日志 - 记录用户的所有操作行为
    用于审计和追溯
    """

    ACTION_CHOICES = (
        ('新增', '新增'),
        ('修改', '修改'),
        ('删除', '删除'),
        ('查询', '查询'),
        ('导出', '导出'),
        ('导入', '导入'),
        ('登录', '登录'),
        ('登出', '登出'),
        ('其他', '其他'),
    )

    STATUS_CHOICES = (
        ('0', '成功'),
        ('1', '失败'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="操作人"
    )
    username = models.CharField("操作账号", max_length=150, blank=True)
    module = models.CharField("操作模块", max_length=50)
    action = models.CharField("操作类型", max_length=20, choices=ACTION_CHOICES)
    description = models.TextField("操作描述", blank=True)

    # 请求信息
    method = models.CharField("请求方法", max_length=10, blank=True)
    url = models.CharField("请求URL", max_length=255, blank=True)
    ip_address = models.GenericIPAddressField("IP地址", null=True, blank=True)
    user_agent = models.CharField("浏览器", max_length=255, blank=True)
    request_params = models.TextField("请求参数", blank=True)

    # 响应信息
    response_data = models.TextField("响应数据", blank=True)
    status = models.CharField("操作状态", max_length=1, choices=STATUS_CHOICES, default='0')
    error_msg = models.TextField("错误信息", blank=True)

    # 时间信息
    created_at = models.DateTimeField("操作时间", auto_now_add=True, db_index=True)
    duration = models.IntegerField("执行时长(ms)", default=0)

    class Meta:
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        db_table = "sys_operation_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['module', '-created_at']),
        ]

    def __str__(self):
        return f"{self.username} {self.action} {self.module} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


# 5. 新增：登录日志模型
class LoginLog(models.Model):
    """
    登录日志 - 记录用户登录行为
    用于安全审计和异常检测
    """

    STATUS_CHOICES = (
        ('0', '成功'),
        ('1', '失败'),
    )

    username = models.CharField("登录账号", max_length=150)
    ip_address = models.GenericIPAddressField("登录IP", null=True, blank=True)
    login_location = models.CharField("登录地点", max_length=100, blank=True)

    # 浏览器信息
    browser = models.CharField("浏览器", max_length=100, blank=True)
    os = models.CharField("操作系统", max_length=50, blank=True)
    device = models.CharField("设备类型", max_length=50, blank=True)

    # 登录状态
    status = models.CharField("登录状态", max_length=1, choices=STATUS_CHOICES)
    msg = models.CharField("提示信息", max_length=255, blank=True)

    # 时间信息
    login_time = models.DateTimeField("登录时间", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
        db_table = "sys_login_log"
        ordering = ["-login_time"]
        indexes = [
            models.Index(fields=['-login_time']),
            models.Index(fields=['username', '-login_time']),
            models.Index(fields=['status', '-login_time']),
        ]

    def __str__(self):
        status_text = "成功" if self.status == '0' else "失败"
        return f"{self.username} 登录{status_text} - {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"
