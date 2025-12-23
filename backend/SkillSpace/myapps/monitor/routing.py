# monitor/routing.py
"""
监控系统 WebSocket 路由配置
"""
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/monitor/system/$", consumers.SystemMonitorConsumer.as_asgi()),
]
