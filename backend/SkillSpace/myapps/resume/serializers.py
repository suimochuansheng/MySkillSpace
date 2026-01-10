# 文件路径: backend/myapps/resume/serializers.py
from rest_framework import serializers


class ResumeDiagnosisSerializer(serializers.Serializer):
    # ⚠️ 必须是 FileField，名字必须是 resume_file
    resume_file = serializers.FileField(required=True, error_messages={"required": "请上传简历文件 (.pdf/.txt)"})

    # ⚠️ 必须是 CharField，不要改成 FileField
    jd_text = serializers.CharField(required=True, error_messages={"required": "职位描述(JD)不能为空"})
