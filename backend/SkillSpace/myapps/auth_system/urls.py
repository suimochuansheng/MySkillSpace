from auth_system.views import (
    CurrentUserView,
    GetRoutersView,
    LoginLogViewSet,
    MenuManagementViewSet,
    OperationLogViewSet,
    RoleManagementViewSet,
    UserLoginView,
    UserLogoutView,
    UserManagementViewSet,
    UserRegistrationView,
)
from django.urls import path
from rest_framework.routers import DefaultRouter

# 创建路由器用于ViewSet
router = DefaultRouter()
router.register(r"users", UserManagementViewSet, basename="user")
router.register(r"roles", RoleManagementViewSet, basename="role")
router.register(r"menus", MenuManagementViewSet, basename="menu")
router.register(r"operationlogs", OperationLogViewSet, basename="operationlog")
router.register(r"loginlogs", LoginLogViewSet, basename="loginlog")

urlpatterns = [
    # 认证相关
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="current_user"),  # 获取当前用户信息
    path("getRouters/", GetRoutersView.as_view(), name="get_routers"),
]

# 添加ViewSet路由
urlpatterns += router.urls
