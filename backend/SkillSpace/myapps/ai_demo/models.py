# ai_demo/models.py
from django.conf import settings
from django.db import models

# Create your models here.


class AITask(models.Model):
    """
    AI 任务记录表（用于追踪和监控）
    """

    STATUS_CHOICES = (
        ("pending", "等待中"),
        ("processing", "处理中"),
        ("completed", "已完成"),
        ("failed", "失败"),
    )

    task_id = models.CharField(max_length=100, unique=True, db_index=True, help_text="任务唯一标识")
    celery_task_id = models.CharField(max_length=100, db_index=True, help_text="Celery任务ID")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_tasks",
        help_text="发起任务的用户（可为空，支持匿名）",
    )
    session_id = models.CharField(max_length=100, db_index=True, help_text="会话ID")
    prompt = models.TextField(help_text="用户提问")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", help_text="任务状态")
    ws_url = models.CharField(max_length=500, help_text="WebSocket连接地址")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="完成时间")
    error_message = models.TextField(blank=True, help_text="错误信息")

    class Meta:
        ordering = ["-created_at"]  # 按创建时间倒序
        verbose_name = "AI任务"
        verbose_name_plural = "AI任务"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["session_id", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "匿名用户"
        return f"[{self.status}] {username} - {self.task_id[:8]}..."


class ChatRecord(models.Model):
    """
    对话记录表
    """

    session_id = models.CharField(max_length=100, db_index=True, help_text="会话ID，用于区分不同用户的对话")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_records",
        help_text="对话用户（可为空，支持匿名）",
    )
    role = models.CharField(max_length=20, choices=(("user", "User"), ("assistant", "AI")), help_text="角色")
    content = models.TextField(help_text="对话内容")
    is_hidden = models.BooleanField(default=False, db_index=True, help_text="是否隐藏此记录（软删除）")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")

    class Meta:
        ordering = ["created_at"]  # 按时间正序排列
        verbose_name = "对话记录"
        verbose_name_plural = "对话记录"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["session_id", "created_at"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "匿名用户"
        return f"{username} - {self.role} - {self.content[:30]}..."
