# resume/models.py
from django.db import models

class ResumeItem(models.Model):
    """
    简历条目模型
    存储个人简历信息
    """
    name = models.CharField(max_length=100, default="我的名字", verbose_name="姓名")
    position = models.CharField(max_length=100, default="我的职位", verbose_name="职位")
    education = models.TextField(default="教育背景", verbose_name="教育经历")
    experience = models.TextField(default="工作经验", verbose_name="工作经验")
    skills = models.TextField(default="技能列表", verbose_name="技能")

    class Meta:
        verbose_name = "简历条目"
        verbose_name_plural = "简历条目"

    def __str__(self):
        # 显示为 "姓名 - 职位"
        return f"{self.name} - {self.position}"