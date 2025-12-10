# ai_chat/model_loader.py
import os
import traceback
from threading import Lock, Thread

import bitsandbytes as bnb
import torch
from modelscope import snapshot_download
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TextIteratorStreamer,
)

model_lock = Lock()

# --------------------------
# 模型配置
# --------------------------
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
MODEL_CACHE_DIR = "./qwen_model_cache"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
MAX_PROMPT_LENGTH = 2000  # 与API限制保持一致

# 全局变量：模型和tokenizer
model = None
tokenizer = None
model_loaded = False

# 环境变量控制是否启用模型加载（默认启用真实模型）
ENABLE_MODEL_LOADING = os.getenv("ENABLE_AI_MODEL", "true").lower() == "true"

print(
    f"当前运行环境：torch={torch.__version__} | bitsandbytes={bnb.__version__} | CUDA={torch.version.cuda}"
)
print(f"AI模型加载开关：{'启用（后台线程加载）' if ENABLE_MODEL_LOADING else '禁用'}")


def load_model_on_startup():
    """
    在应用启动时加载模型（由apps.py调用）
    此函数在后台线程中运行，不会阻塞Django启动
    """
    global model, tokenizer, model_loaded

    if not ENABLE_MODEL_LOADING:
        print("提示：AI模型加载已禁用，如需启用请设置环境变量 ENABLE_AI_MODEL=true")
        return

    print("🔄 开始加载 AI 模型...")
    try:
        # 下载模型
        model_dir = snapshot_download(
            MODEL_NAME, cache_dir=MODEL_CACHE_DIR, revision="master"
        )

        # 加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_dir, trust_remote_code=True, padding_side="right", use_fast=False
        )

        # 量化配置
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float32,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        print("⏳ 正在加载模型 (FP32 Compute Mode)...")
        model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            device_map=DEVICE,
            trust_remote_code=True,
            quantization_config=bnb_config,
        ).eval()

        model_loaded = True
        print("✅ 模型加载完成！AI功能已就绪")

    except Exception as e:
        print(f"❌ 模型加载失败：{str(e)}")
        traceback.print_exc()
        model_loaded = False


def get_model():
    """
    获取已加载的模型和tokenizer
    如果模型未加载或加载失败，抛出异常
    """
    if not ENABLE_MODEL_LOADING:
        raise RuntimeError("AI模型加载未启用，请设置环境变量 ENABLE_AI_MODEL=true")

    if not model_loaded or model is None or tokenizer is None:
        raise RuntimeError("模型未成功加载，请检查启动日志")

    return model, tokenizer


# --------------------------
# 核心修改点 1: 修改系统提示词，加入思考过程指令
# --------------------------
SYSTEM_PROMPT = """你是一个乐于助人的AI助手。
请按照以下格式回答用户的问题：

思考：<在这里写出你的思考过程，包括分析用户意图、问题拆解、推理步骤等>

答案：<在这里给出最终的完整答案>

注意：
1. 必须严格按照上述格式输出
2. 思考部分要详细展示你的推理过程
3. 答案部分要清晰、准确、完整
"""


def generate_answer(prompt: str, history: list = None) -> str:
    """
    生成回答
    :param prompt: 当前用户问题
    :param history: 历史对话列表 [{"role": "user", "content": "..."}, ...]
    """
    # 输入验证
    if not prompt.strip():
        return "请输入有效的问题！"
    if len(prompt) > MAX_PROMPT_LENGTH:
        return f"输入过长（当前{len(prompt)}字），请控制在{MAX_PROMPT_LENGTH}字以内"

    # 初始化历史
    if history is None:
        history = []

    # 获取已加载的模型
    try:
        loaded_model, loaded_tokenizer = get_model()
    except RuntimeError as e:
        return f"模型未启用：{str(e)}"

    with model_lock:
        try:
            # 构建包含历史记录的消息列表
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # 追加历史记录 (限制最近 10 轮，防止显存爆满)
            for msg in history[-10:]:
                role = "user" if msg.get("role") == "user" else "assistant"
                messages.append({"role": role, "content": msg.get("content")})

            # 追加当前问题
            messages.append({"role": "user", "content": prompt})

            text = loaded_tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

            # 编码输入
            encoding = loaded_tokenizer([text], return_tensors="pt")
            input_ids = encoding.input_ids.to(DEVICE)
            attention_mask = encoding.attention_mask.to(DEVICE)

            # 生成配置
            generated_ids = loaded_model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_new_tokens=1024,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.05,
                pad_token_id=loaded_tokenizer.eos_token_id,
            )

            # 解码输出
            generated_ids = [
                output_ids[len(input_ids) :]
                for input_ids, output_ids in zip(input_ids, generated_ids)
            ]
            answer = loaded_tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]
            return answer

        except Exception as e:
            traceback.print_exc()
            return f"生成出错：{str(e)}"
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


def stream_generate_answer(prompt: str, history: list = None):
    """
    流式生成回答的生成器函数
    Yields:
        dict: {"token": "片段", "type": "thinking" | "answer"}
    """
    if history is None:
        history = []

    # 获取已加载的模型
    try:
        loaded_model, loaded_tokenizer = get_model()
    except RuntimeError as e:
        yield {"token": f"模型未启用：{str(e)}", "type": "answer"}
        return

    # 1. 构建 Prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-10:]:
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("content")})
    messages.append({"role": "user", "content": prompt})

    text = loaded_tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    inputs = loaded_tokenizer([text], return_tensors="pt").to(DEVICE)

    # 2. 初始化流式迭代器
    streamer = TextIteratorStreamer(
        loaded_tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    # 3. 配置生成参数
    generation_kwargs = dict(
        inputs,
        streamer=streamer,
        max_new_tokens=1024,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=loaded_tokenizer.eos_token_id,
    )

    # 4. 在独立线程中启动生成
    thread = Thread(target=loaded_model.generate, kwargs=generation_kwargs)
    thread.start()

    # 5. 主线程从 streamer 中读取 token，并根据"思考："和"答案："标记切换类型
    current_type = "thinking"  # 默认先输出思考过程
    full_content = ""

    for new_text in streamer:
        full_content += new_text

        # 检测是否遇到"答案："标记，切换到answer类型
        if "答案：" in full_content and current_type == "thinking":
            # 找到"答案："的位置
            answer_pos = full_content.find("答案：")

            # 如果当前token跨越了"答案："分界线，需要分段处理
            before_answer = full_content[: answer_pos + len("答案：")]
            current_len_before_token = len(full_content) - len(new_text)

            if current_len_before_token < answer_pos + len("答案："):
                # 当前token包含了"答案："标记
                # 将"答案："之前的部分作为thinking
                thinking_part_len = (
                    answer_pos + len("答案：") - current_len_before_token
                )
                if thinking_part_len > 0 and thinking_part_len <= len(new_text):
                    thinking_part = new_text[:thinking_part_len]
                    answer_part = new_text[thinking_part_len:]

                    # 先发送thinking部分（包含"答案："标记）
                    if thinking_part:
                        yield {"token": thinking_part, "type": "thinking"}

                    # 切换类型
                    current_type = "answer"

                    # 发送answer部分
                    if answer_part:
                        yield {"token": answer_part, "type": "answer"}
                    continue

            # 切换类型（适用于"答案："已经在之前的token中完整出现的情况）
            current_type = "answer"

        # 正常发送token
        yield {"token": new_text, "type": current_type}
