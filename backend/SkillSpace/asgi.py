"""
ASGI config for SkillSpace project.

支持 HTTP 和 WebSocket 协议路由
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SkillSpace.settings")

# 初始化 Django ASGI 应用（必须在导入 routing 之前）
django_asgi_app = get_asgi_application()

# 导入 WebSocket 路由（在 Django 初始化之后）
from SkillSpace.myapps.ai_demo import routing as ai_routing
from SkillSpace.myapps.monitor import routing as monitor_routing

# ASGI 应用配置
application = ProtocolTypeRouter(
    {
        # HTTP 请求使用标准 Django ASGI
        "http": django_asgi_app,
        # WebSocket 请求使用 Channels
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    ai_routing.websocket_urlpatterns
                    + monitor_routing.websocket_urlpatterns
                )
            )
        ),
    }
)
