from django.urls import path
from .views import ResumeDiagnosisView

urlpatterns = [
    # path('resume/', ResumeListAPIView.as_view(), name='resume-list'),
    # 新增的 AI 诊断接口
    path("diagnose/", ResumeDiagnosisView.as_view(), name="resume-diagnose"),
]
