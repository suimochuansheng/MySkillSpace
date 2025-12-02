# tasks_hub/models.py
from django.db import models

class AsyncTask(models.Model):
    """
    异步任务模型
    记录各种异步任务的执行状态
    """
    TASK_TYPES = [
        ('file', '文件处理'),
        ('data', '数据获取'),
        ('email', '邮件发送'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('error', '错误'),
    ]
    
    task_id = models.CharField(max_length=255, unique=True, verbose_name="任务ID")
    task_type = models.CharField(max_length=10, choices=TASK_TYPES, verbose_name="任务类型")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "异步任务"
        verbose_name_plural = "异步任务"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.get_status_display()}"