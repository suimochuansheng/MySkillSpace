# ai_demo/views.py
# AI模型接口视图，提供通义千问对话服务

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

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
    POST /api/ai/qwen/
    请求体: {"prompt": "你的问题"}
    响应: {"code": 200, "msg": "success", "data": "回答内容"}
    """
    http_method_names = ['post']

    def post(self, request):
        # 获取用户问题
        prompt = request.data.get("prompt", "").strip()
        
        # 校验输入
        if not prompt:
            return Response(
                {"code": 400, "msg": "请输入问题内容！", "data": ""},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 限制输入长度（防止过长输入）
        if len(prompt) > 2000:
            return Response(
                {"code": 400, "msg": "问题内容过长，请控制在2000字以内！", "data": ""},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 调用AI模型生成回答
            if MODEL_AVAILABLE:
                answer = generate_answer(prompt)
            else:
                # Mock模式（模型未加载时用于测试）
                answer = f"[模拟回答] 您的问题是: {prompt}\n\n这是一个模拟回答，实际环境中将调用Qwen-7B-Chat模型生成内容。"
            
            logger.info(f"AI对话 - 问题: {prompt[:50]}... | 回答长度: {len(answer)}")
            
            return Response(
                {"code": 200, "msg": "success", "data": answer},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            # 异常处理
            logger.error(f"AI推理失败: {str(e)}")
            return Response(
                {"code": 500, "msg": f"模型推理出错: {str(e)}", "data": ""},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )