# auth_system/urls.py
"""
用户认证系统的URL路由配置
定义所有认证相关的API端点
"""
from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    CurrentUserView,
    PasswordChangeView,
    CheckEmailView,
)

# 应用命名空间（用于reverse URL）
app_name = 'auth_system'

urlpatterns = [
    # 用户注册
    # POST /api/auth/register/
    # path('register/', UserRegistrationView.as_view(), name='register'),
    
    # 用户登录
    # POST /api/auth/login/
    path('login/', UserLoginView.as_view(), name='login'),
    
    # 用户登出
    # POST /api/auth/logout/
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # 获取当前用户信息
    # GET /api/auth/me/
    # path('me/', CurrentUserView.as_view(), name='current-user'),
    
    # 修改密码
    # POST /api/auth/password/change/
    # path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    
    # 检查邮箱是否可用
    # POST /api/auth/check-email/
    # path('check-email/', CheckEmailView.as_view(), name='check-email'),
]
                                       