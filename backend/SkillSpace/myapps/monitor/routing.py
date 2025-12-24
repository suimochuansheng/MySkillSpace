# monitor/routing.py
"""
监控系统 WebSocket 路由配置
"""
from django.urls import re_path

from . import cloud_consumers  # 新增
from . import consumers

websocket_urlpatterns = [
    # Windows本地监控路由
    re_path(r"ws/monitor/system/$", consumers.SystemMonitorConsumer.as_asgi()),
    # 云服务器监控路由（新增）
    # URL格式：ws://host/ws/monitor/cloud/<server_name>/
    # 例如：ws://localhost:8000/ws/monitor/cloud/生产服务器/
    re_path(
        r"ws/monitor/cloud/(?P<server_name>[\w\-\u4e00-\u9fa5]+)/$",
        cloud_consumers.CloudMonitorConsumer.as_asgi(),
    ),
]
