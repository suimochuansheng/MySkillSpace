# resume/views.py
from rest_framework import generics
from .models import ResumeItem
from .serializers import ResumeSerializer

class ResumeListAPIView(generics.ListAPIView):
    """
    GET /api/resume/
    返回所有简历条目
    """
    queryset = ResumeItem.objects.all()
    serializer_class = ResumeSerializer
    pagination_class = None  # 禁用分页
