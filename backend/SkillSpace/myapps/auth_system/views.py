# auth_system/views.py
"""
用户认证系统的API视图
提供用户注册、登录、登出、获取用户信息等接口
"""
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordChangeSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    用户注册API
    
    POST /api/auth/register/
    
    请求体:
        {
            "email": "user@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "username": "用户名" (可选)
        }
    
    成功响应 (201):
        {
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "用户名",
                "date_joined": "2025-11-30T12:00:00Z"
            },
            "message": "注册成功"
        }
    
    失败响应 (400):
        {
            "email": ["该邮箱已被注册"],
            "password_confirm": ["两次密码不一致"]
        }
    """
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # 允许任何人访问注册接口
    
    def create(self, request, *args, **kwargs):
        """
        处理用户注册请求
        
        流程:
            1. 验证输入数据（邮箱格式、密码强度等）
            2. 检查邮箱是否已被注册
            3. 创建新用户（密码自动加密）
            4. 返回用户信息
        """
        # 使用序列化器验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 创建用户
        user = serializer.save()
        
        # 返回成功响应
        return Response({
            'user': UserSerializer(user).data,
            'message': '注册成功，欢迎加入 Skillspace！'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    用户登录API
    
    POST /api/auth/login/
    
    请求体:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    
    成功响应 (200):
        {
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "用户名",
                "last_login": "2025-11-30T12:00:00Z"
            },
            "message": "登录成功"
        }
    
    失败响应 (400):
        {
            "detail": "邮箱或密码错误，请重试"
        }
    """
    
    permission_classes = [permissions.AllowAny]  # 允许任何人访问登录接口
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        """
        处理用户登录请求
        
        流程:
            1. 验证邮箱和密码
            2. 使用Django的authenticate进行认证
            3. 检查账户状态（是否被禁用）
            4. 创建会话（Session）
            5. 返回用户信息
        """
        # 使用序列化器验证登录凭证
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        # 验证数据（会调用authenticate）
        serializer.is_valid(raise_exception=True)
        
        # 获取验证通过的用户对象
        user = serializer.validated_data['user']
        
        # 创建登录会话（Django Session）
        # 这会在数据库中创建session记录，并设置cookie
        login(request, user)
        
        # 返回成功响应
        return Response({
            'user': UserSerializer(user).data,
            'message': '登录成功！🎉 欢迎回到 Skillspace！'
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    """
    用户登出API
    
    POST /api/auth/logout/
    
    请求头:
        需要在已登录状态下访问（携带Session Cookie）
    
    成功响应 (200):
        {
            "message": "登出成功"
        }
    """
    
    permission_classes = [permissions.IsAuthenticated]  # 只有已登录用户可以登出
    
    def post(self, request):
        """
        处理用户登出请求
        
        流程:
            1. 检查用户是否已登录
            2. 清除Session数据
            3. 删除Session Cookie
            4. 返回成功响应
        """
        # 执行登出操作（清除session）
        logout(request)
        
        # 返回成功响应
        return Response({
            'message': '登出成功，期待您的再次访问！'
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    获取当前登录用户信息API
    
    GET /api/auth/me/
    
    请求头:
        需要在已登录状态下访问（携带Session Cookie）
    
    成功响应 (200):
        {
            "id": 1,
            "email": "user@example.com",
            "username": "用户名",
            "date_joined": "2025-11-30T12:00:00Z",
            "last_login": "2025-11-30T12:30:00Z"
        }
    
    未登录响应 (401):
        {
            "detail": "身份验证凭据未提供。"
        }
    """
    
    permission_classes = [permissions.IsAuthenticated]  # 只有已登录用户可以访问
    
    def get(self, request):
        """
        返回当前登录用户的详细信息
        
        流程:
            1. 检查用户是否已登录
            2. 序列化用户数据
            3. 返回用户信息
        """
        # 获取当前登录用户
        user = request.user
        
        # 序列化用户数据
        serializer = UserSerializer(user)
        
        # 返回用户信息
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    """
    修改密码API
    
    POST /api/auth/password/change/
    
    请求头:
        需要在已登录状态下访问（携带Session Cookie）
    
    请求体:
        {
            "old_password": "oldpassword123",
            "new_password": "newpassword456",
            "new_password_confirm": "newpassword456"
        }
    
    成功响应 (200):
        {
            "message": "密码修改成功，请使用新密码登录"
        }
    
    失败响应 (400):
        {
            "old_password": ["当前密码错误"],
            "new_password_confirm": ["两次新密码不一致"]
        }
    """
    
    permission_classes = [permissions.IsAuthenticated]  # 只有已登录用户可以修改密码
    
    def post(self, request):
        """
        处理修改密码请求
        
        流程:
            1. 验证旧密码是否正确
            2. 验证新密码格式和一致性
            3. 更新密码（自动加密）
            4. 清除当前会话（需要重新登录）
            5. 返回成功响应
        """
        # 使用序列化器验证数据
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        # 验证数据
        serializer.is_valid(raise_exception=True)
        
        # 保存新密码
        serializer.save()
        
        # 修改密码后自动登出（安全措施）
        logout(request)
        
        # 返回成功响应
        return Response({
            'message': '密码修改成功，请使用新密码重新登录'
        }, status=status.HTTP_200_OK)


class CheckEmailView(APIView):
    """
    检查邮箱是否已被注册API
    
    POST /api/auth/check-email/
    
    请求体:
        {
            "email": "user@example.com"
        }
    
    成功响应 (200):
        {
            "available": true,  # true表示可用，false表示已被注册
            "message": "该邮箱可以使用"
        }
    """
    
    permission_classes = [permissions.AllowAny]  # 允许任何人检查邮箱
    
    def post(self, request):
        """
        检查邮箱是否可用
        用于前端实时验证，提升用户体验
        
        流程:
            1. 获取邮箱地址
            2. 查询数据库检查是否存在
            3. 返回可用性状态
        """
        email = request.data.get('email', '')
        
        # 检查邮箱格式
        if not email:
            return Response({
                'available': False,
                'message': '请输入邮箱地址'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查邮箱是否已存在（不区分大小写）
        exists = User.objects.filter(email__iexact=email).exists()
        
        # 返回检查结果
        return Response({
            'available': not exists,
            'message': '该邮箱已被注册' if exists else '该邮箱可以使用'
        }, status=status.HTTP_200_OK)
