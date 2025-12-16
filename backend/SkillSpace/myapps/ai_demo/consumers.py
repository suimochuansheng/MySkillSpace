# ai_demo/consumers.py
"""
WebSocket Consumer - 处理 AI 流式响应的 WebSocket 连接
"""

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class AIChatConsumer(AsyncWebsocketConsumer):
    """
    AI 对话 WebSocket Consumer

    工作流程：
    1. 前端连接 WebSocket: ws://localhost:8000/ws/ai/<task_id>/
    2. Consumer 加入 Redis Channel: ai_<task_id>
    3. Celery Worker 推送消息到 Channel
    4. Consumer 转发消息给前端
    """

    async def connect(self):
        """建立 WebSocket 连接"""
        # 从 URL 获取 task_id
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]
        self.channel_name_prefix = f"ai_{self.task_id}"

        # 加入 Channel Group（用于接收 Celery 推送的消息）
        await self.channel_layer.group_add(
            self.channel_name_prefix,
            self.channel_name
        )

        # 接受 WebSocket 连接
        await self.accept()

        logger.info(f"✅ WebSocket 连接建立: task_id={self.task_id}")

    async def disconnect(self, close_code):
        """断开 WebSocket 连接"""
        # 离开 Channel Group
        await self.channel_layer.group_discard(
            self.channel_name_prefix,
            self.channel_name
        )

        logger.info(f"❌ WebSocket 连接断开: task_id={self.task_id}, code={close_code}")

    async def receive(self, text_data):
        """
        接收来自前端的消息（暂不处理，仅用于心跳检测）
        """
        try:
            data = json.loads(text_data)
            if data.get("type") == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
        except Exception as e:
            logger.error(f"接收消息错误: {e}")

    async def ai_message(self, event):
        """
        接收来自 Celery (通过 Channel Layer) 的消息并转发给前端

        event 格式:
        {
            "type": "ai_message",  # 必须匹配方法名（下划线分隔）
            "token": "你",
            "chunk_type": "answer",
            "task_id": "xxx"
        }
        """
        # 转发给前端
        await self.send(text_data=json.dumps({
            "code": 200,
            "token": event["token"],
            "type": event["chunk_type"],
            "task_id": event.get("task_id", self.task_id)
        }))
