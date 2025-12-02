# resume/serializers.py
from rest_framework import serializers
from .models import ResumeItem

class ResumeSerializer(serializers.ModelSerializer):
    """
    简历条目序列化器
    """
    class Meta:
        model = ResumeItem
        fields = '__all__'