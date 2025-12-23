# backend/SkillSpace/myapps/ai_demo/ai_engine.py

import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class QwenEngine:
    """
    Qwen (通义千问) 模型引擎 - 单例模式
    确保一个 Celery Worker 进程只加载一次模型到显存
    """

    _instance = None
    model = None
    tokenizer = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        print("🚀 [GPU Worker] 正在初始化 AI 引擎，加载模型中...")
        try:
            # 这里替换为您本地模型的真实路径，或者 ModelScope/HuggingFace 的模型ID
            # 例如: "Qwen/Qwen2.5-1.5B-Instruct"
            model_path = "Qwen/Qwen2.5-1.5B-Instruct"

            # 检查 GPU 是否可用
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"🖥️  检测到运行设备: {device} (RTX 3080 应该显示 cuda)")

            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path, trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",  # 自动分配到 GPU
                trust_remote_code=True,
                torch_dtype=torch.float16,  # 使用半精度节省显存
            )
            print("✅ [GPU Worker] 模型加载完成！")
        except Exception as e:
            print(f"❌ [GPU Worker] 模型加载失败: {e}")
            # 开发阶段为了不报错，可以先 mock 一个
            self.model = "MockModel"

    def chat(self, prompt):
        """
        执行推理
        """
        if self.model == "MockModel":
            time.sleep(2)
            return f"【测试模式】收到提示词：{prompt}。CUDA未正确加载，这是模拟返回。"

        # 真实的推理逻辑
        messages = [
            {"role": "system", "content": "你是一个专业的简历分析助手。"},
            {"role": "user", "content": prompt},
        ]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to("cuda")

        generated_ids = self.model.generate(model_inputs.input_ids, max_new_tokens=512)
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        return response


# 全局预加载实例
# 注意：Python 的模块加载机制保证了这是线程安全的
# 但为了控制加载时机，我们在 Task 里调用 get_instance() 更好
