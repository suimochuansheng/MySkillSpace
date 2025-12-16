# ai_demo/routing.py
"""
WebSocket URL 路由配置
"""

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    # WebSocket 路由：ws://localhost:8000/ws/ai/<task_id>/
    path("ws/ai/<str:task_id>/", consumers.AIChatConsumer.as_asgi()),
]
