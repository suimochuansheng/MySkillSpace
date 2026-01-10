# ai_demo/views.py
# AI模型接口视图，提供通义千问对话服务
import json
import logging
import uuid

from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# 导入流式生成函数
from .model_loader import stream_generate_answer
from .models import AITask, ChatRecord
from .serializers import ChatRecordSerializer, ChatRequestSerializer

# 导入 Celery 任务
from .tasks import qwen_chat_task_streaming

logger = logging.getLogger(__name__)


class AITaskListAPI(APIView):
    """
    AI 任务列表查询接口

    GET /api/ai/tasks/
    查询参数：
        - user_only: true/false (是否只查看自己的任务，默认 true)
        - status: pending/processing/completed/failed (按状态筛选)
        - limit: 数量限制（默认 20）

    返回示例：
    {
        "code": 200,
        "data": [
            {
                "task_id": "abc-123",
                "user": "张三",
                "prompt": "介绍Python",
                "status": "processing",
                "created_at": "2025-12-14 10:30:00"
            }
        ]
    }
    """

    def get(self, request):
        # 获取查询参数
        user_only = request.query_params.get("user_only", "true").lower() == "true"
        status_filter = request.query_params.get("status", None)
        limit = int(request.query_params.get("limit", 20))

        # 构建查询
        queryset = AITask.objects.all()

        # 如果只查看自己的任务（且已登录）
        if user_only and request.user.is_authenticated:
            queryset = queryset.filter(user=request.user)
        elif user_only and not request.user.is_authenticated:
            # 未登录用户只能查看匿名任务（如果有 session_id 可以根据 session 查）
            queryset = queryset.filter(user__isnull=True)

        # 按状态筛选
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 限制数量
        tasks = queryset[:limit]

        # 构建返回数据
        data = []
        for task in tasks:
            data.append(
                {
                    "task_id": task.task_id,
                    "celery_task_id": task.celery_task_id,
                    "user": task.user.username if task.user else "匿名用户",
                    "session_id": task.session_id,
                    "prompt": (task.prompt[:100] + "..." if len(task.prompt) > 100 else task.prompt),
                    "status": task.status,
                    "status_display": task.get_status_display(),
                    "ws_url": task.ws_url,
                    "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "completed_at": (task.completed_at.strftime("%Y-%m-%d %H:%M:%S") if task.completed_at else None),
                }
            )

        return Response({"code": 200, "msg": "success", "data": data, "count": len(data)})


@method_decorator(csrf_exempt, name="dispatch")
class QwenChatAsyncAPI(APIView):
    """
    通义千问异步对话接口 (Celery + WebSocket 方案 B)

    POST /api/ai/qwen-async/
    请求体: {"prompt": "...", "session_id": "..."}
    返回: {"code": 200, "task_id": "xxx", "ws_url": "ws://..."}

    前端流程：
    1. POST 请求此接口，获得 task_id 和 ws_url
    2. 建立 WebSocket 连接到 ws_url
    3. 实时接收流式响应
    """

    authentication_classes = []

    def post(self, request):
        # 1. 验证参数
        request_serializer = ChatRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                {"code": 400, "msg": str(request_serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 获取验证后的数据
        prompt = request_serializer.validated_data["prompt"]
        session_id = request_serializer.validated_data.get("session_id") or str(uuid.uuid4())

        try:
            # 2. 获取当前登录用户（如果已登录）
            current_user = request.user if request.user.is_authenticated else None

            # 3. 保存用户提问到数据库
            ChatRecord.objects.create(session_id=session_id, role="user", content=prompt, user=current_user)

            # 4. 获取历史上下文
            history_objs = ChatRecord.objects.filter(session_id=session_id).order_by("created_at")
            history_data = [{"role": r.role, "content": r.content} for r in history_objs]

            # 5. 生成唯一的 task_id
            task_id = str(uuid.uuid4())

            # 6. 构建 WebSocket URL（根据实际部署环境调整）
            ws_protocol = "ws"  # 生产环境使用 wss
            host = request.get_host()  # 获取当前主机名
            ws_url = f"{ws_protocol}://{host}/ws/ai/{task_id}/"

            # 7. 提交 Celery 异步任务
            task = qwen_chat_task_streaming.delay(
                task_id=task_id,
                prompt=prompt,
                session_id=session_id,
                history=history_data,
            )

            # 8. 保存任务记录到数据库（重要！用于追踪和监控）
            ai_task = AITask.objects.create(
                task_id=task_id,
                celery_task_id=task.id,
                user=current_user,
                session_id=session_id,
                prompt=prompt[:500],  # 只保存前500字符
                status="pending",
                ws_url=ws_url,
            )

            username = current_user.username if current_user else "匿名用户"
            logger.info(f"✅ 任务已创建: user={username}, task_id={task_id}, celery_id={task.id}")

            # 9. 返回任务信息
            return Response(
                {
                    "code": 200,
                    "msg": "任务已提交到异步队列",
                    "data": {
                        "task_id": task_id,
                        "celery_task_id": task.id,
                        "session_id": session_id,
                        "ws_url": ws_url,
                        "user": username,  # 返回用户名，方便前端显示
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"系统错误: {str(e)}")
            return Response(
                {"code": 500, "msg": f"系统内部错误: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class QwenChatAPI(APIView):
    """
    通义千问双模对话接口 (支持流式 SSE 和 阻塞式 REST) - 原方案 A
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
        records = ChatRecord.objects.filter(session_id=session_id).order_by("created_at")
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
        session_id = request_serializer.validated_data.get("session_id") or str(uuid.uuid4())
        stream_mode = request_serializer.validated_data.get("stream", True)  # 获取流式开关

        try:
            # 2. 保存用户提问到数据库 (立即保存)
            ChatRecord.objects.create(session_id=session_id, role="user", content=prompt)

            # 3. 获取历史上下文
            history_objs = ChatRecord.objects.filter(session_id=session_id).order_by("created_at")
            history_data = [{"role": r.role, "content": r.content} for r in history_objs]

            # 4. 调用真实模型生成器（如果模型未启用将抛出错误）
            generator = stream_generate_answer(prompt, history=history_data)

            # =================================================
            # 分支 A: 流式响应 (SSE) - 适用于前端实时交互
            # =================================================
            if stream_mode:

                def event_stream():
                    full_answer = ""  # 只保存答案部分
                    thinking_content = ""  # 单独保存思考过程
                    try:
                        for chunk in generator:
                            token = chunk["token"]
                            chunk_type = chunk["type"]

                            # 分别累积思考和答案内容
                            if chunk_type == "thinking":
                                thinking_content += token
                            elif chunk_type == "answer":
                                full_answer += token

                            # SSE 格式: data: {json}\n\n
                            yield f"data: {json.dumps({'code': 200, 'token': token, 'type': chunk_type})}\n\n"

                            # 如果模型生成器已经发送finish信号，直接结束
                            if chunk_type == "finish":
                                break

                        # 流结束后保存完整回答到数据库（只保存答案部分，不保存思考过程）
                        # 这样历史上下文更简洁，加载时不会混淆
                        if full_answer:
                            ChatRecord.objects.create(
                                session_id=session_id,
                                role="assistant",
                                content=full_answer,
                            )

                        logger.info(
                            f"AI对话完成(Stream) - Session: {session_id}, 思考长度: {len(thinking_content)}, 答案长度: {len(full_answer)}"
                        )

                    except Exception as e:
                        logger.error(f"Stream Error: {e}")
                        yield f"data: {json.dumps({'code': 500, 'msg': str(e), 'type': 'error'})}\n\n"

                response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
                # 禁用缓存确保实时性
                response["Cache-Control"] = "no-cache"
                response["X-Accel-Buffering"] = "no"
                return response

            # =================================================
            # 分支 B: 阻塞式响应 (JSON) - 适用于API调用/脚本
            # =================================================
            else:
                full_answer = ""  # 只保存答案部分
                thinking_content = ""  # 单独保存思考过程

                # 手动消耗生成器，分别拼接思考和答案
                for chunk in generator:
                    if chunk["type"] == "thinking":
                        thinking_content += chunk["token"]
                    elif chunk["type"] == "answer":
                        full_answer += chunk["token"]

                # 保存答案到数据库（不保存思考过程）
                if full_answer:
                    ChatRecord.objects.create(session_id=session_id, role="assistant", content=full_answer)

                logger.info(
                    f"AI对话完成(Block) - Session: {session_id}, 思考长度: {len(thinking_content)}, 答案长度: {len(full_answer)}"
                )

                return Response(
                    {
                        "code": 200,
                        "msg": "success",
                        "data": full_answer,  # 只返回答案
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
