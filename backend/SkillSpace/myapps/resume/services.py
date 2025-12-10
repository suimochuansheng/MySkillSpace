# 文件路径: backend/myapps/resume/services.py

from openai import OpenAI
import os
import json


# 推荐模型：
# qwen-plus (性价比高，能力强)
# qwen-max (能力最强，稍贵)
# qwen-turbo (最快最便宜)
MODEL_NAME = "qwen-plus"
# ===========================================


def ai_analyze_resume(resume_text: str, jd_text: str) -> dict:
    """
    调用阿里云通义千问模型进行简历诊断
    """

    # 构造 Prompt (提示词)
    # 这里的 Prompt 不需要变，通义千问完全听得懂
    prompt = f"""
    你是一个资深的技术面试官。请对比以下【简历】和【岗位描述(JD)】。
    
    【岗位描述】：
    {jd_text}
    
    【简历内容】：
    {resume_text}
    
    【任务】：
    1. 给简历打分（0-100）。
    2. 分析简历的亮点（Pros）和不足（Cons）。
    3. 给出具体的修改建议。
    
    【输出格式】：
    必须返回标准的 JSON 格式，包含以下字段：score, summary, pros(list), cons(list), suggestions。
    不要返回 Markdown 格式（如 ```json ... ```），直接返回 JSON 字符串。
    """
    # 获取密钥和地址
    ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY")
    ALIYUN_BASE_URL = os.getenv("ALIYUN_BASE_URL")
    try:
        # 初始化客户端（使用 openai 库，但指向阿里云）
        client = OpenAI(api_key=ALIYUN_API_KEY, base_url=ALIYUN_BASE_URL)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个能够输出结构化 JSON 数据的助手。",
                },
                {"role": "user", "content": prompt},
            ],
            # 这里的 response_format 设置取决于模型版本，Qwen 新版支持很好
            # 如果报错，可以去掉下面这一行，靠 Prompt 约束即可
            response_format={"type": "json_object"},
        )

        # 获取返回内容
        content = response.choices[0].message.content

        # 解析 JSON
        # 有时候模型还是会顽皮地加上 ```json 头，这里做个清洗保险
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        print(f"阿里云接口返回内容: {json.loads(content)}")
        return json.loads(content)

    except Exception as e:
        print(f"阿里云接口调用失败: {e}")
        # 这里返回 Mock 数据，保证前端不崩
        return {
            "score": 0,
            "summary": f"服务暂时不可用: {str(e)}",
            "pros": [],
            "cons": [],
            "suggestions": "请检查后端 API Key 配置。",
        }
