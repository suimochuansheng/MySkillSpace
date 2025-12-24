"""
云服务器监控 WebSocket Consumer
处理前端连接并推送实时监控数据
"""

import hashlib
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class CloudMonitorConsumer(AsyncWebsocketConsumer):
    """
    云服务器监控 WebSocket Consumer
    每个客户端连接会创建一个实例
    """

    async def connect(self):
        """客户端连接时调用"""
        # 从URL获取服务器名称
        # URL格式：ws://host/ws/monitor/cloud/{server_name}/
        self.server_name = self.scope["url_route"]["kwargs"]["server_name"]
        # 将服务器名称转换为URL安全的ASCII字符（支持中文）
        self.room_group_name = (
            f"cloud_monitor_{hashlib.md5(self.server_name.encode()).hexdigest()}"
        )

        logger.info(
            f"WebSocket连接请求: 服务器={self.server_name}, group={self.room_group_name}"
        )

        # 加入频道组
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 接受WebSocket连接
        await self.accept()

        # 发送连接成功消息
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "message": f"已连接到云服务器监控: {self.server_name}",
                    "server_name": self.server_name,
                }
            )
        )

        logger.info(f"WebSocket连接成功: {self.server_name}")

    async def disconnect(self, close_code):
        """客户端断开连接时调用"""
        logger.info(f"WebSocket断开连接: {self.server_name}, code={close_code}")

        # 离开频道组
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        接收来自客户端的消息（可选）

        Args:
            text_data: 客户端发送的JSON字符串
        """
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "")

            logger.debug(f"收到客户端消息: type={message_type}")

            # 处理心跳检测
            if message_type == "ping":
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "pong",
                            "message": "服务器响应正常",
                            "timestamp": data.get("timestamp"),
                        }
                    )
                )

            # 处理其他控制消息（可扩展）
            elif message_type == "get_status":
                # 客户端请求立即获取状态（可选功能）
                await self.send(
                    text_data=json.dumps(
                        {"type": "info", "message": "请等待下一次数据推送"}
                    )
                )

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            await self.send(
                text_data=json.dumps({"type": "error", "message": "无效的消息格式"})
            )
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": f"服务器错误: {str(e)}"}
                )
            )

    async def cloud_status_update(self, event):
        """
        接收来自后台任务的云服务器状态更新
        通过 channel_layer.group_send() 调用此方法

        Args:
            event: 包含type和data的字典
        """
        logger.debug(f"推送数据到客户端: {self.server_name}")

        # 发送云服务器状态数据到 WebSocket
        await self.send(
            text_data=json.dumps({"type": "cloud_status", "data": event["data"]})
        )
