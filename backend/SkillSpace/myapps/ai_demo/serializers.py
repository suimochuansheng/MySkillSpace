# ai_demo/serializers.py
# AI对话记录序列化器

from rest_framework import serializers
from .models import ChatRecord


class ChatRecordSerializer(serializers.ModelSerializer):
    """
    对话记录序列化器
    用于序列化和反序列化对话历史数据
    """
    
    class Meta:
        model = ChatRecord
        fields = ['id', 'session_id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_role(self, value):
        """验证角色字段"""
        if value not in ['user', 'assistant']:
            raise serializers.ValidationError("角色必须是 'user' 或 'assistant'")
        return value
    
    def validate_content(self, value):
        """验证内容字段"""
        if not value.strip():
            raise serializers.ValidationError("对话内容不能为空")
        if len(value) > 10000:
            raise serializers.ValidationError("对话内容过长，请控制在10000字以内")
        return value


class ChatRequestSerializer(serializers.Serializer):
    """
    对话请求序列化器
    用于验证用户的对话请求参数
    """
    prompt = serializers.CharField(
        required=True,
        max_length=2000,
        error_messages={
            'required': '请输入问题内容',
            'max_length': '问题内容过长，请控制在2000字以内'
        }
    )
    session_id = serializers.CharField(
        required=False,
        max_length=100,
        help_text="会话ID，如未提供则自动生成"
    )
    
    def validate_prompt(self, value):
        """验证问题内容"""
        if not value.strip():
            raise serializers.ValidationError("请输入问题内容")
        return value.strip()
