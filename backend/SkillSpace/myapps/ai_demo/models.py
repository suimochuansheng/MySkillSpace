# ai_demo/models.py
from django.db import models

# Create your models here.



class ChatRecord(models.Model):
    """
    对话记录表
    """

    session_id = models.CharField(
        max_length=100, db_index=True, help_text="会话ID，用于区分不同用户的对话"
    )
    role = models.CharField(
        max_length=20, choices=(("user", "User"), ("assistant", "AI")), help_text="角色"
    )
    content = models.TextField(help_text="对话内容")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")

    class Meta:
        ordering = ["created_at"]  # 按时间正序排列
        verbose_name = "对话记录"
