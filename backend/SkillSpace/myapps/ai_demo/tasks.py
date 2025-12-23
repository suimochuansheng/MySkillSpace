# backend/SkillSpace/myapps/ai_demo/tasks.py

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from .model_loader import stream_generate_answer

# 获取 Channel Layer 实例（用于向 WebSocket 推送消息）
channel_layer = get_channel_layer()


@shared_task(name="myapps.ai_demo.tasks.qwen_chat_task_streaming", bind=True)
def qwen_chat_task_streaming(self, task_id, prompt, session_id=None, history=None):
    """
    AI 流式对话任务（通过 WebSocket 推送）

    参数：
        task_id: 任务唯一标识（用于 WebSocket Channel 命名）
        prompt: 用户提问
        session_id: 会话ID（可选，用于保存历史记录）
        history: 历史对话记录（可选）

    工作流程：
        1. Celery Worker 接收任务
        2. 调用 AI 模型流式生成
        3. 每生成一个 token 就推送到 Redis Channel
        4. WebSocket Consumer 监听 Channel 并转发给前端
    """
    print(f"📥 [Celery Task] 开始执行流式任务: task_id={task_id}")

    if history is None:
        history = []

    # Channel Group 名称（与 Consumer 中保持一致）
    channel_group_name = f"ai_{task_id}"

    try:
        # 调用模型的流式生成器
        generator = stream_generate_answer(prompt, history=history)

        # 遍历生成器，逐 token 推送
        for chunk in generator:
            token = chunk["token"]
            chunk_type = chunk["type"]

            # 通过 Channel Layer 推送消息到 WebSocket Consumer
            async_to_sync(channel_layer.group_send)(
                channel_group_name,
                {
                    "type": "ai_message",  # 对应 Consumer 的 ai_message 方法
                    "token": token,
                    "chunk_type": chunk_type,
                    "task_id": task_id,
                },
            )

            # 如果收到结束信号，停止推送
            if chunk_type == "finish":
                print(f"✅ [Celery Task] 任务完成: task_id={task_id}")
                break

        # (可选) 保存完整对话记录到数据库
        # if session_id:
        #     from .models import ChatRecord
        #     ChatRecord.objects.create(...)

        return {"status": "success", "task_id": task_id}

    except Exception as e:
        print(f"❌ [Celery Task] 任务失败: {str(e)}")

        # 发送错误消息到前端
        async_to_sync(channel_layer.group_send)(
            channel_group_name,
            {
                "type": "ai_message",
                "token": f"系统错误: {str(e)}",
                "chunk_type": "error",
                "task_id": task_id,
            },
        )

        return {"status": "error", "error": str(e)}


# 保留原有的非流式任务（用于批量处理场景）
@shared_task(name="myapps.ai_demo.tasks.qwen_chat_task", bind=True)
def qwen_chat_task(self, prompt, resume_id=None):
    """
    AI 对话/分析任务（非流式，返回最终结果）
    适用于批量处理场景
    """
    print(f"📥 [Task] 收到 AI 任务，简历ID: {resume_id}")

    try:
        # 调用流式生成器并拼接完整结果
        generator = stream_generate_answer(prompt, history=[])
        full_result = ""

        for chunk in generator:
            if chunk["type"] in ["answer", "thinking"]:
                full_result += chunk["token"]

        print(f"📤 [Task] 推理完成，结果长度: {len(full_result)}")

        return {"status": "success", "result": full_result}

    except Exception as e:
        print(f"❌ [Task Error] {str(e)}")
        return {"status": "error", "error": str(e)}
