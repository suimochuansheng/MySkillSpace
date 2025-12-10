# 文件路径: backend/myapps/resume/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ResumeDiagnosisSerializer
from .utils import extract_text_from_file
from .services import ai_analyze_resume


class ResumeDiagnosisView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        # 打印一下接收到的数据，方便你在终端调试
        print("接收到的数据 Keys:", request.data.keys())

        serializer = ResumeDiagnosisSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # 注意：这里取值必须是用 resume_file
                resume_file = serializer.validated_data["resume_file"]
                jd_text = serializer.validated_data["jd_text"]

                resume_content = extract_text_from_file(resume_file)

                if not resume_content or len(resume_content) < 10:
                    return Response(
                        {"code": 400, "message": "文件解析为空"}, status=400
                    )

                result = ai_analyze_resume(resume_content, jd_text)
                return Response({"code": 200, "data": result})
            except Exception as e:
                return Response({"code": 500, "message": str(e)}, status=500)

        # 打印具体的错误信息到终端
        print("校验失败 Errors:", serializer.errors)
        return Response(
            {"code": 400, "message": "参数校验错误", "errors": serializer.errors},
            status=400,
        )
