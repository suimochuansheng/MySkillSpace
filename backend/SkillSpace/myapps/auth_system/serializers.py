# auth_system/serializers.py
"""
用户认证系统的序列化器
处理用户数据的序列化和反序列化，用于API数据传输
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    用户基础信息序列化器
    用于返回用户信息（不包含密码）
    
    返回字段:
        id: 用户ID
        email: 邮箱地址
        username: 用户名
        date_joined: 注册时间
        last_login: 最后登录时间
    """
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    处理新用户注册请求
    
    输入字段:
        email: 邮箱地址（必填）
        password: 密码（必填，写入时不返回）
        password_confirm: 确认密码（必填，仅用于验证）
        username: 用户名（可选）
    """
    
    # 密码字段（write_only表示仅写入，不在响应中返回）
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text='密码至少6位'
    )
    
    # 确认密码字段（仅用于验证，不存入数据库）
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='再次输入密码以确认'
    )
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm']
    
    def validate_email(self, value):
        """
        验证邮箱是否已被注册
        
        参数:
            value: 待验证的邮箱地址
            
        返回:
            验证通过的邮箱地址
            
        异常:
            ValidationError: 如果邮箱已存在
        """
        # 检查邮箱是否已存在（不区分大小写）
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('该邮箱已被注册，请使用其他邮箱')
        return value
    
    def validate(self, attrs):
        """
        整体数据验证
        验证两次密码是否一致
        
        参数:
            attrs: 所有输入的数据字典
            
        返回:
            验证通过的数据
            
        异常:
            ValidationError: 如果两次密码不一致
        """
        # 验证两次密码是否一致
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '两次输入的密码不一致'
            })
        
        # 移除password_confirm字段（不需要存入数据库）
        attrs.pop('password_confirm')
        
        return attrs
    
    def create(self, validated_data):
        """
        创建新用户
        使用UserManager的create_user方法确保密码被正确加密
        
        参数:
            validated_data: 验证通过的数据
            
        返回:
            创建的User对象
        """
        # 使用自定义UserManager创建用户（会自动加密密码）
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data.get('username', '')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    验证登录凭证（邮箱或用户名 + 密码）
    
    输入字段:
        account: 邮箱地址或用户名
        password: 密码
        
    返回字段:
        user: 用户信息对象
        token: 认证令牌（如果使用Token认证）
    """
    
    # 账户字段（支持邮箱或用户名）
    account = serializers.CharField(
        required=True,
        help_text='登录账户（邮箱地址或用户名）'
    )
    
    # 密码字段
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='登录密码'
    )
    
    # 用户对象（验证成功后填充，仅读）
    user = UserSerializer(read_only=True)
    
    def validate(self, attrs):
        """
        验证登录凭证
        支持使用邮箱或用户名登录
        
        参数:
            attrs: 包含account和password的字典
            
        返回:
            包含user对象的字典
            
        异常:
            ValidationError: 如果账户或密码错误
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        account = attrs.get('account')
        password = attrs.get('password')
        
        # 判断输入的是邮箱还是用户名
        user = None
        
        # 尝试通过邮箱查找用户
        if '@' in account:
            try:
                user_obj = User.objects.get(email=account)
                # 使用Django的authenticate方法验证密码
                user = authenticate(
                    request=self.context.get('request'),
                    username=user_obj.email,  # USERNAME_FIELD是email
                    password=password
                )
            except User.DoesNotExist:
                pass
        else:
            # 尝试通过用户名查找用户
            try:
                user_obj = User.objects.get(username=account)
                # 使用Django的authenticate方法验证密码
                user = authenticate(
                    request=self.context.get('request'),
                    username=user_obj.email,  # USERNAME_FIELD是email，所以传入email
                    password=password
                )
            except User.DoesNotExist:
                pass
        
        # 验证失败处理
        if not user:
            raise serializers.ValidationError({
                'detail': '账户或密码错误，请重试'
            })
        
        # 检查账户是否被禁用
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': '该账户已被禁用，请联系管理员'
            })
        
        # 将验证成功的用户对象添加到attrs中
        attrs['user'] = user
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """
    修改密码序列化器
    用于已登录用户修改密码
    
    输入字段:
        old_password: 旧密码
        new_password: 新密码
        new_password_confirm: 确认新密码
    """
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='当前密码'
    )
    
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text='新密码（至少6位）'
    )
    
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='确认新密码'
    )
    
    def validate_old_password(self, value):
        """
        验证旧密码是否正确
        
        参数:
            value: 输入的旧密码
            
        返回:
            验证通过的旧密码
            
        异常:
            ValidationError: 如果旧密码错误
        """
        user = self.context['request'].user
        
        # 检查旧密码是否正确
        if not user.check_password(value):
            raise serializers.ValidationError('当前密码错误')
        
        return value
    
    def validate(self, attrs):
        """
        验证新密码
        确保两次输入的新密码一致
        
        参数:
            attrs: 所有输入数据
            
        返回:
            验证通过的数据
            
        异常:
            ValidationError: 如果两次新密码不一致
        """
        # 验证两次新密码是否一致
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': '两次输入的新密码不一致'
            })
        
        # 移除确认密码字段
        attrs.pop('new_password_confirm')
        
        return attrs
    
    def save(self):
        """
        保存新密码
        
        返回:
            更新后的用户对象
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
