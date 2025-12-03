from django.urls import path
from .views import QwenChatAPI

urlpatterns = [
    path('qwen/', QwenChatAPI.as_view(), name='qwen-chat'),
]