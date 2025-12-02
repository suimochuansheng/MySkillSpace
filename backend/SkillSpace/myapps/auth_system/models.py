# auth_system/models.py
"""
用户认证系统的数据模型
包含自定义用户模型，使用邮箱作为主要登录方式
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    自定义用户管理器
    用于创建普通用户和超级用户
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        创建并保存普通用户
        
        参数:
            email: 用户邮箱（必填，作为唯一标识）
            password: 用户密码
            **extra_fields: 其他用户字段（如username等）
            
        返回:
            User对象
        """
        if not email:
            raise ValueError('用户必须提供邮箱地址')
        
        # 标准化邮箱地址（转小写）
        email = self.normalize_email(email)
        
        # 创建用户实例
        user = self.model(email=email, **extra_fields)
        
        # 设置加密密码
        user.set_password(password)
        
        # 保存到数据库
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        创建并保存超级用户
        自动设置 is_staff 和 is_superuser 为 True
        
        参数:
            email: 超级用户邮箱
            password: 超级用户密码
            **extra_fields: 其他字段
            
        返回:
            超级用户对象
        """
        # 设置超级用户必需权限
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # 验证权限设置
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置 is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型
    使用邮箱作为唯一标识符，支持用户名可选
    
    字段说明:
        email: 邮箱地址（唯一，用于登录）
        username: 用户名（可选，用于显示）
        is_active: 账户是否激活
        is_staff: 是否是管理员
        date_joined: 注册时间
        last_login: 最后登录时间（继承自AbstractBaseUser）
    """
    
    # 邮箱字段（主要登录凭证）
    email = models.EmailField(
        verbose_name='邮箱地址',
        max_length=255,
        unique=True,  # 邮箱必须唯一
        db_index=True,  # 创建索引以提高查询性能
        help_text='用户登录时使用的邮箱地址'
    )
    
    # 用户名字段（可选，但可用于登录）
    username = models.CharField(
        verbose_name='用户名',
        max_length=150,
        blank=True,  # 允许为空
        null=True,
        db_index=True,  # 创建索引以提高查询性能
        help_text='用户显示名称，可用于登录'
    )
    
    # 账户状态字段
    is_active = models.BooleanField(
        verbose_name='账户激活状态',
        default=True,
        help_text='取消选择代替删除账户'
    )
    
    # 管理员权限字段
    is_staff = models.BooleanField(
        verbose_name='管理员状态',
        default=False,
        help_text='指定用户是否可以登录管理后台'
    )
    
    # 注册时间
    date_joined = models.DateTimeField(
        verbose_name='注册时间',
        default=timezone.now,
        help_text='用户首次创建账户的时间'
    )
    
    # 社交登录字段（预留用于Google/GitHub登录）
    oauth_provider = models.CharField(
        verbose_name='OAuth提供商',
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('google', 'Google'),
            ('github', 'GitHub'),
        ],
        help_text='第三方登录平台（如Google、GitHub）'
    )
    
    oauth_id = models.CharField(
        verbose_name='OAuth用户ID',
        max_length=255,
        blank=True,
        null=True,
        help_text='第三方平台返回的用户唯一标识'
    )
    
    # 指定自定义的用户管理器
    objects = UserManager()
    
    # 配置：使用email作为登录字段
    USERNAME_FIELD = 'email'
    
    # 配置：创建超级用户时必须输入的字段（除了email和password）
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户列表'
        db_table = 'auth_user'  # 自定义数据库表名
        ordering = ['-date_joined']  # 默认按注册时间倒序排列
    
    def __str__(self):
        """
        返回用户的字符串表示
        优先显示用户名，如果没有则显示邮箱
        """
        return self.username if self.username else self.email
    
    def get_full_name(self):
        """
        返回用户完整名称
        用于Django Admin等地方显示
        """
        return self.username if self.username else self.email
    
    def get_short_name(self):
        """
        返回用户简短名称
        """
        return self.username if self.username else self.email.split('@')[0]
