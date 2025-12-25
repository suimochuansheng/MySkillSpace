# backend/SkillSpace/myapps/ai_demo/api_engine.py
"""
阿里云通义千问 API 引擎（流式对话）
用于云端部署，无需本地 GPU
"""
import os
import re

from openai import OpenAI


def stream_generate_answer_api(prompt: str, history: list = None):
    """
    使用阿里云通义千问 API 进行流式对话

    参数：
        prompt: 用户输入
        history: 历史对话记录

    返回：
        生成器，逐token返回结果
    """
    if history is None:
        history = []

    # 获取 API 配置
    ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY")
    ALIYUN_BASE_URL = os.getenv("ALIYUN_BASE_URL")
    MODEL_NAME = os.getenv("ALIYUN_MODEL_NAME", "qwen-plus")  # 默认使用 qwen-plus

    if not ALIYUN_API_KEY or not ALIYUN_BASE_URL:
        yield {
            "token": "系统提示：阿里云 API 未配置，请检查环境变量 ALIYUN_API_KEY 和 ALIYUN_BASE_URL",
            "type": "answer",
        }
        yield {"token": "", "type": "finish"}
        return

    # 系统提示词
    SYSTEM_PROMPT = """你是一个乐于助人的AI助手。
请按照以下格式回答用户的问题，务必严格遵守标记格式：

<thinking>
在这里写出你的详细思考过程、分析步骤
</thinking>

<answer>
在这里给出最终的完整答案
</answer>

注意：
1. 必须使用<thinking>和<answer>标记
2. thinking标记内写思考过程
3. answer标记内写最终答案
"""

    try:
        # 初始化 OpenAI 客户端（指向阿里云）
        client = OpenAI(api_key=ALIYUN_API_KEY, base_url=ALIYUN_BASE_URL)

        # 构建消息
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # 添加历史记录（限制最近10轮）
        for msg in history[-10:]:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("content")})

        messages.append({"role": "user", "content": prompt})

        # 调用流式 API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
            temperature=0.7,
            top_p=0.8,
            max_tokens=2048,
        )

        # 解析流式输出
        current_type = "thinking"  # 当前状态：thinking/answer/none
        in_thinking = False
        in_answer = False
        buffer = ""

        # 预编译正则表达式
        thinking_start_pattern = re.compile(r"<thinking>")
        thinking_end_pattern = re.compile(r"</thinking>")
        answer_start_pattern = re.compile(r"<answer>")
        answer_end_pattern = re.compile(r"</answer>")

        for chunk in response:
            if chunk.choices[0].delta.content is None:
                continue

            new_text = chunk.choices[0].delta.content
            buffer += new_text

            # 检测<thinking>开始标记
            if not in_thinking and thinking_start_pattern.search(buffer):
                in_thinking = True
                current_type = "thinking"
                buffer = re.sub(r".*?<thinking>", "", buffer)
                continue

            # 检测</thinking>结束标记
            if in_thinking and thinking_end_pattern.search(buffer):
                in_thinking = False
                current_type = "none"
                buffer = re.sub(r"</thinking>.*", "", buffer)
                if buffer:
                    yield {"token": buffer, "type": "thinking"}
                buffer = ""
                continue

            # 检测<answer>开始标记
            if not in_answer and answer_start_pattern.search(buffer):
                in_answer = True
                current_type = "answer"
                buffer = re.sub(r".*?<answer>", "", buffer)
                continue

            # 检测</answer>结束标记
            if in_answer and answer_end_pattern.search(buffer):
                in_answer = False
                current_type = "none"
                buffer = re.sub(r"</answer>.*", "", buffer)
                if buffer:
                    yield {"token": buffer, "type": "answer"}
                buffer = ""
                continue

            # 推送正常内容
            if current_type in ["thinking", "answer"] and buffer:
                # 避免标记被拆分
                if not buffer.endswith("<") and not buffer.endswith("</"):
                    yield {"token": buffer, "type": current_type}
                    buffer = ""

        # 处理剩余缓冲区
        if buffer:
            yield {
                "token": buffer,
                "type": current_type if current_type != "none" else "answer",
            }

        # 流结束后发送 finish 信号
        yield {"token": "", "type": "finish"}

    except Exception as e:
        print(f"❌ [API Engine] 调用失败: {str(e)}")
        yield {"token": f"系统错误: {str(e)}", "type": "error"}
        yield {"token": "", "type": "finish"}
