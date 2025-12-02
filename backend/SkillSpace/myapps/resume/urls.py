from django.urls import path
from .views import ResumeListAPIView

urlpatterns = [
    path('resume/', ResumeListAPIView.as_view(), name='resume-list'),
]