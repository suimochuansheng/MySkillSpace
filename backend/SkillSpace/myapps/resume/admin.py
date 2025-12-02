# resume/admin.py
from django.contrib import admin
from .models import ResumeItem

@admin.register(ResumeItem)
class ResumeItemAdmin(admin.ModelAdmin):
    """
    简历条目管理界面
    """
    list_display = ('name', 'position', 'skills')
    search_fields = ('name', 'position', 'skills')
    list_filter = ('position',)