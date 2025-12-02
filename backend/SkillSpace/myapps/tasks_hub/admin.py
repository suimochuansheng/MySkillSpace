# tasks_hub/admin.py
from django.contrib import admin
from .models import AsyncTask

@admin.register(AsyncTask)
class AsyncTaskAdmin(admin.ModelAdmin):
    """
    异步任务管理界面
    """
    list_display = ('task_id', 'task_type', 'status', 'created_at')
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = ('task_id',)
    readonly_fields = ('task_id', 'created_at')
    ordering = ('-created_at',)
