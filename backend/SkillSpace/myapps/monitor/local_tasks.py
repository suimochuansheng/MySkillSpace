"""
Linux本地系统监控后台任务
定期采集本地Linux系统数据并通过 WebSocket 推送给前端
"""

import logging
import threading
import time
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .local_collectors import get_local_collector

logger = logging.getLogger(__name__)


class LocalMonitorTask:
    """Linux本地系统监控后台任务"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.channel_layer = get_channel_layer()
        self.collector = get_local_collector()

    def start(self):
        """启动后台监控线程"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("Linux本地系统监控后台任务已启动")

    def stop(self):
        """停止后台监控线程"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Linux本地系统监控后台任务已停止")

    def _run(self):
        """后台线程运行方法"""
        while self.running:
            try:
                # 采集系统数据
                system_data = self.collector.collect_all()

                # 通过 Channel Layer 发送数据到 WebSocket
                # 使用与Windows监控相同的group名称,实现无缝切换
                async_to_sync(self.channel_layer.group_send)(
                    "system_monitor",
                    {"type": "system_status_update", "data": system_data},
                )

                logger.debug("Linux本地监控数据推送成功")

                # 等待1秒后继续下一次采集
                time.sleep(1)

            except Exception as e:
                logger.error(f"Linux本地监控任务出错: {e}")
                time.sleep(1)


# 全局单例
_local_monitor_task = None


def get_local_monitor_task() -> LocalMonitorTask:
    """
    获取Linux本地监控任务单例

    Returns:
        LocalMonitorTask实例
    """
    global _local_monitor_task
    if _local_monitor_task is None:
        _local_monitor_task = LocalMonitorTask()
    return _local_monitor_task


def reset_local_monitor_task():
    """
    重置Linux本地监控任务单例（主要用于测试）
    """
    global _local_monitor_task
    if _local_monitor_task:
        _local_monitor_task.stop()
    _local_monitor_task = None
