# ai_demo/views.py
# AI模型接口视图，提供通义千问对话服务

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging
import uuid

from .models import ChatRecord
from .serializers import ChatRecordSerializer, ChatRequestSerializer

try:
    from .model_loader import generate_answer
    MODEL_AVAILABLE = True
except Exception as e:
    MODEL_AVAILABLE = False
    logging.warning(f"AI模型加载失败，将使用Mock模式: {str(e)}")

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class QwenChatAPI(APIView):
    """
    通义千问对话接口
    GET /api/ai/qwen/?session_id=xxx  -> 获取历史记录
    POST /api/ai/qwen/ -> 发送消息
    请求体: {"prompt": "你的问题", "session_id": "可选的会话ID"}
    """
    # 限制该视图接受 GET 和 POST 方法
    http_method_names = ['get', 'post']

    def get(self, request):
        """获取历史对话记录"""
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"code": 400, "msg": "缺少 session_id 参数", "data": []}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 查询数据库中的历史记录
        records = ChatRecord.objects.filter(session_id=session_id).order_by('created_at')
        serializer = ChatRecordSerializer(records, many=True)
        
        logger.info(f"获取历史记录 - Session: {session_id} | 记录数: {records.count()}")
        
        return Response({
            "code": 200, 
            "msg": "success", 
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        # 使用序列化器验证请求数据
        request_serializer = ChatRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                {"code": 400, "msg": str(request_serializer.errors), "data": ""},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取验证后的数据
        prompt = request_serializer.validated_data['prompt']
        # 如果前端没传 session_id，生成一个临时的（建议前端生成并存储在 localStorage）
        session_id = request_serializer.validated_data.get('session_id', str(uuid.uuid4()))
        
        try:
                        # 1. 保存用户提问到数据库
            ChatRecord.objects.create(
                session_id=session_id,
                role='user',
                content=prompt
            )

            # 2. 获取历史上下文 (用于多轮对话)
            # 获取最近 10 条记录，转换为列表字典格式供模型使用
            history_objs = ChatRecord.objects.filter(session_id=session_id).order_by('created_at')
            # 转换为 list[dict]
            history_data = [
                {"role": r.role, "content": r.content} 
                for r in history_objs
            ]
            # 3. 调用模型生成回答
            if MODEL_AVAILABLE:
                # 注意：这里 generate_answer 已经修改为接受 history 参数
                answer = generate_answer(prompt, history=history_data)
            else:
                # Mock模式（模型未加载时用于测试）
                answer = f"<think>正在模拟思考过程...\n分析用户意图：{prompt}</think>[Mock] 这是模拟回答。"

            # 4. 保存 AI 回答到数据库
            ChatRecord.objects.create(
                session_id=session_id,
                role='assistant',
                content=answer
            )
                
            logger.info(f"AI对话完成 - Session: {session_id} | 长度: {len(answer)}")


            return Response(
                {
                    "code": 200, 
                    "msg": "success", 
                    "data": answer,
                    "session_id": session_id # 返回 ID 供前端下次使用
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"AI推理失败: {str(e)}")
            return Response(
                {"code": 500, "msg": f"系统内部错误: {str(e)}", "data": ""},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )