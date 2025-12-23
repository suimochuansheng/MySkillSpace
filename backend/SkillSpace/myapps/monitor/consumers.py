# monitor/consumers.py
"""
系统监控 WebSocket Consumer
实现实时推送系统状态数据到前端
"""
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class SystemMonitorConsumer(AsyncWebsocketConsumer):
    """
    系统监控 WebSocket Consumer
    每个客户端连接会创建一个实例
    """

    async def connect(self):
        """客户端连接时调用"""
        # 加入系统监控频道组
        self.room_group_name = "system_monitor"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 接受 WebSocket 连接
        await self.accept()

        # 发送连接成功消息
        await self.send(
            text_data=json.dumps(
                {"type": "connection_established", "message": "已连接到系统监控服务"}
            )
        )

    async def disconnect(self, close_code):
        """客户端断开连接时调用"""
        # 离开系统监控频道组
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """接收来自客户端的消息（可选）"""
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "")

            # 处理客户端发来的控制消息（如暂停/恢复）
            if message_type == "ping":
                await self.send(
                    text_data=json.dumps({"type": "pong", "message": "服务器响应正常"})
                )
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "无效的消息格式"})
            )

    async def system_status_update(self, event):
        """
        接收来自后台线程的系统状态更新
        通过 channel_layer.group_send() 调用此方法
        """
        # 发送系统状态数据到 WebSocket
        await self.send(
            text_data=json.dumps({"type": "system_status", "data": event["data"]})
        )
