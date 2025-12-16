from django.urls import path

from .views import QwenChatAPI, QwenChatAsyncAPI, AITaskListAPI

urlpatterns = [
    # 原有接口（方案 A：同步流式 SSE）
    path("qwen/", QwenChatAPI.as_view(), name="qwen-chat"),
    # 新增接口（方案 B：Celery + WebSocket）
    path("qwen-async/", QwenChatAsyncAPI.as_view(), name="qwen-chat-async"),
    # 任务列表查询接口
    path("tasks/", AITaskListAPI.as_view(), name="ai-task-list"),
]
