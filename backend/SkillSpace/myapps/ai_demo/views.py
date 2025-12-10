# ai_demo/views.py
# AI模型接口视图，提供通义千问对话服务
import json
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse
import logging
import uuid

from .models import ChatRecord
from .serializers import ChatRecordSerializer, ChatRequestSerializer


# 导入流式生成函数
from .model_loader import stream_generate_answer

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class QwenChatAPI(APIView):
    """
    通义千问双模对话接口 (支持流式 SSE 和 阻塞式 REST)
    POST /api/ai/qwen/
    请求体: {"prompt": "...", "session_id": "...", "stream": true/false}
    """

    # 添加这行：指定认证类为空，或者仅使用 BasicAuth/TokenAuth
    # 只要不包含 SessionAuthentication，DRF 就不会强制检查 CSRF
    authentication_classes = []

    http_method_names = ["get", "post"]

    def get(self, request):
        """获取历史对话记录（兼容旧前端）"""
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"code": 400, "msg": "缺少 session_id 参数", "data": []},
                status=status.HTTP_400_BAD_REQUEST,
            )
        records = ChatRecord.objects.filter(session_id=session_id).order_by(
            "created_at"
        )
        serializer = ChatRecordSerializer(records, many=True)
        return Response(
            {"code": 200, "msg": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        # 1. 验证参数
        request_serializer = ChatRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                {"code": 400, "msg": str(request_serializer.errors), "data": ""},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 获取验证后的数据
        prompt = request_serializer.validated_data["prompt"]
        session_id = request_serializer.validated_data.get("session_id") or str(
            uuid.uuid4()
        )
        stream_mode = request_serializer.validated_data.get(
            "stream", True
        )  # 获取流式开关

        try:
            # 2. 保存用户提问到数据库 (立即保存)
            ChatRecord.objects.create(
                session_id=session_id, role="user", content=prompt
            )

            # 3. 获取历史上下文
            history_objs = ChatRecord.objects.filter(session_id=session_id).order_by(
                "created_at"
            )
            history_data = [
                {"role": r.role, "content": r.content} for r in history_objs
            ]

            # 4. 调用真实模型生成器（如果模型未启用将抛出错误）
            generator = stream_generate_answer(prompt, history=history_data)

            # =================================================
            # 分支 A: 流式响应 (SSE) - 适用于前端实时交互
            # =================================================
            if stream_mode:

                def event_stream():
                    full_answer = ""
                    try:
                        for chunk in generator:
                            token = chunk["token"]
                            full_answer += token
                            # SSE 格式: data: {json}\n\n
                            yield f"data: {json.dumps({'code': 200, 'token': token, 'type': chunk['type']})}\n\n"

                        # 流结束后保存完整回答到数据库
                        ChatRecord.objects.create(
                            session_id=session_id, role="assistant", content=full_answer
                        )
                        # 发送结束信号
                        yield f"data: {json.dumps({'code': 200, 'token': '', 'type': 'finish'})}\n\n"

                    except Exception as e:
                        logger.error(f"Stream Error: {e}")
                        yield f"data: {json.dumps({'code': 500, 'msg': str(e)})}\n\n"

                response = StreamingHttpResponse(
                    event_stream(), content_type="text/event-stream"
                )
                # 禁用缓存确保实时性
                response["Cache-Control"] = "no-cache"
                response["X-Accel-Buffering"] = "no"
                return response

            # =================================================
            # 分支 B: 阻塞式响应 (JSON) - 适用于API调用/脚本
            # =================================================
            else:
                full_answer = ""
                thinking_content = ""

                # 手动消耗生成器，拼接完整结果
                for chunk in generator:
                    if chunk["type"] == "thinking":
                        thinking_content += chunk["token"]
                    full_answer += chunk["token"]

                # 保存完整回答到数据库
                ChatRecord.objects.create(
                    session_id=session_id, role="assistant", content=full_answer
                )

                logger.info(f"AI对话完成(Block) - Session: {session_id}")

                return Response(
                    {
                        "code": 200,
                        "msg": "success",
                        "data": full_answer,
                        "session_id": session_id,
                        "thinking": thinking_content,  # 额外返回思考过程供调试
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            logger.error(f"系统错误: {str(e)}")
            return Response(
                {"code": 500, "msg": f"系统内部错误: {str(e)}", "data": ""},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
