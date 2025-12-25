# ai_chat/model_loader.py
import os
import re
import traceback
from threading import Lock, Thread

from django.conf import settings  # 引入 Django settings 以获取基准路径

# 条件导入 AI 依赖（仅在可用时导入）
try:
    import torch
    from modelscope import snapshot_download
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TextIteratorStreamer,
    )

    AI_AVAILABLE = True
except ImportError:
    # AI 依赖不可用，定义占位符以避免运行时错误
    torch = None
    snapshot_download = None
    AutoModelForCausalLM = None
    AutoTokenizer = None
    BitsAndBytesConfig = None
    TextIteratorStreamer = None
    AI_AVAILABLE = False

model_lock = Lock()

# --------------------------
# 模型配置
# --------------------------
# 1. 确保缓存目录是绝对路径，避免相对路径带来的混淆
BASE_DIR = settings.BASE_DIR
MODEL_CACHE_DIR = os.path.join(BASE_DIR, "qwen_model_cache")

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
DEVICE = "cuda:0" if (torch and torch.cuda.is_available()) else "cpu"
MAX_PROMPT_LENGTH = 2000

# 全局变量
model = None
tokenizer = None
model_loaded = False

# 环境变量控制
ENABLE_MODEL_LOADING = os.getenv("ENABLE_AI_MODEL", "true").lower() == "true"
USE_AI_API = os.getenv("USE_AI_API", "false").lower() == "true"  # 新增：是否使用 API

# Flash Attention 开关（需要先安装 flash-attn）
# 安装命令：pip install flash-attn --no-build-isolation
ENABLE_FLASH_ATTENTION = os.getenv("ENABLE_FLASH_ATTENTION", "false").lower() == "true"

print(f"AI引擎模式：{'阿里云API' if USE_AI_API else '本地大模型'}")
print(f"AI模型加载开关：{'启用' if ENABLE_MODEL_LOADING else '禁用'}")
print(
    f"Flash Attention: {'启用' if ENABLE_FLASH_ATTENTION else '禁用（安装后可启用）'}"
)


def load_model_on_startup():
    """
    在应用启动时加载模型

    注意：如果使用 API 模式（USE_AI_API=True），则跳过本地模型加载

    优化要点：
    1. 跳过联网验证（local_files_only=True）
    2. 直接指定设备（device_map="cuda:0"）
    3. 关闭双重量化（节省启动时间）
    4. 启用 CUDA 优化
    5. 支持 Flash Attention 2（需要安装）
    """
    global model, tokenizer, model_loaded

    # =========================================================
    # 🚀 如果使用 API 模式，跳过本地模型加载
    # =========================================================
    if USE_AI_API:
        print("[INFO] [ModelLoader] 检测到 USE_AI_API=True，跳过本地模型加载")
        print("[INFO] 将使用阿里云通义千问 API")
        return

    # 检查 AI 依赖是否可用
    if not AI_AVAILABLE:
        print("[WARNING] AI dependencies not installed. Skipping model loading.")
        return

    if not ENABLE_MODEL_LOADING:
        return

    print("[INFO] [ModelLoader] 准备加载本地 AI 模型...")
    print(f"[DIR] 缓存目录: {MODEL_CACHE_DIR}")

    try:
        # =========================================================
        # ⚡ 优化 1: CUDA 性能优化（启动时配置）
        # =========================================================
        if torch.cuda.is_available():
            print("[CONFIG] 启用 CUDA 性能优化...")
            torch.backends.cudnn.benchmark = True  # cuDNN 自动调优
            torch.backends.cuda.matmul.allow_tf32 = True  # TF32 加速（3080 支持）
            torch.backends.cudnn.allow_tf32 = True
            torch.cuda.empty_cache()  # 清理显存
            print(f"[OK] CUDA 优化已启用 (设备: {torch.cuda.get_device_name(0)})")

        # =========================================================
        # ⚡ 优化 2: 直接指定本地路径，跳过 snapshot_download
        # =========================================================
        local_model_path = rf"{MODEL_CACHE_DIR}\Qwen\Qwen2___5-7B-Instruct"

        # 检查路径是否存在
        if os.path.exists(local_model_path) and len(os.listdir(local_model_path)) > 0:
            print(f"[LOAD] 检测到本地模型，跳过联网校验，直接加载: {local_model_path}")
            model_dir = local_model_path
        else:
            print("[WARNING] 本地路径无效，回退到 ModelScope 下载/校验模式...")
            model_dir = snapshot_download(
                MODEL_NAME, cache_dir=MODEL_CACHE_DIR, revision="master"
            )

        # =========================================================
        # ⚡ 优化 3: 加载 Tokenizer（跳过联网验证）
        # =========================================================
        print("[TOKENIZER] 加载 Tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            trust_remote_code=True,
            padding_side="right",
            local_files_only=True,  # [OK] 跳过联网验证
            resume_download=False,  # [OK] 不尝试续传
        )
        print("[OK] Tokenizer 加载完成")

        # =========================================================
        # ⚡ 优化 4: 量化配置（关闭双重量化）
        # =========================================================
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,  # 使用 float16
            bnb_4bit_use_double_quant=False,  # [OK] 关闭双重量化（减少启动时间）
            bnb_4bit_quant_type="nf4",
        )

        # =========================================================
        # ⚡ 优化 5: 加载模型（启用 Flash Attention 2）
        # =========================================================
        print("[LOADING] 正在加载模型到显存 (4-bit 量化)...")

        # 构建模型加载参数
        model_kwargs = {
            "device_map": "cuda:0",  # [OK] 直接指定设备，跳过自动分析
            "trust_remote_code": True,
            "quantization_config": bnb_config,
            "local_files_only": True,  # [OK] 跳过联网验证
            "resume_download": False,  # [OK] 不尝试续传
        }

        # 如果启用 Flash Attention，添加参数
        if ENABLE_FLASH_ATTENTION:
            try:
                import flash_attn  # noqa: F401

                model_kwargs["attn_implementation"] = "flash_attention_2"
                print("[OPTIMIZE] Flash Attention 2 已启用")
            except ImportError:
                print("[WARNING] Flash Attention 未安装，使用标准 Attention")
                print("[TIP] 提示：pip install flash-attn --no-build-isolation")

        model = AutoModelForCausalLM.from_pretrained(model_dir, **model_kwargs).eval()

        model_loaded = True

        # 显示加载信息
        print("✅ 模型加载成功！")
        print(
            f"📊 Attention 实现: {getattr(model.config, '_attn_implementation', 'standard')}"
        )

        # 显示显存使用情况
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated(0) / 1024**3
            reserved = torch.cuda.memory_reserved(0) / 1024**3
            print(
                f"💾 显存占用: {allocated:.2f}GB (已分配) / {reserved:.2f}GB (已预留)"
            )

    except Exception as e:
        print(f"❌ 模型加载失败：{str(e)}")
        traceback.print_exc()
        model_loaded = False


def get_model():
    if not AI_AVAILABLE:
        raise RuntimeError(
            "AI dependencies not installed. Please install required packages."
        )
    if not ENABLE_MODEL_LOADING:
        raise RuntimeError("AI模型加载未启用")
    if not model_loaded or model is None:
        raise RuntimeError("模型尚未加载完成，请稍后再试")
    return model, tokenizer


# --------------------------
# Prompt 和 生成逻辑保持不变
# --------------------------
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


def stream_generate_answer(prompt: str, history: list = None):
    """
    流式生成答案（支持双引擎切换）

    根据环境变量 USE_AI_API 选择：
    - True: 使用阿里云 API（云端部署）
    - False: 使用本地大模型（本地演示）

    优化要点：
    1. 优化生成参数（max_new_tokens, top_p, top_k）
    2. 启用 KV cache
    3. 使用正则预编译
    """
    if history is None:
        history = []

    # =========================================================
    # ⚡ 引擎选择：根据环境变量决定使用 API 还是本地模型
    # =========================================================
    if USE_AI_API:
        print("[INFO] 使用阿里云 API 引擎")
        from .api_engine import stream_generate_answer_api

        yield from stream_generate_answer_api(prompt, history)
        return

    # =========================================================
    # 以下是本地大模型引擎逻辑
    # =========================================================
    print("[INFO] 使用本地大模型引擎")

    try:
        loaded_model, loaded_tokenizer = get_model()
    except RuntimeError as e:
        yield {"token": f"系统提示：{str(e)}", "type": "answer"}
        return

    # =========================================================
    # ⚡ 优化 1: 构建消息（限制历史长度）
    # =========================================================
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-10:]:  # 限制最近 10 轮对话
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("content")})
    messages.append({"role": "user", "content": prompt})

    text = loaded_tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    inputs = loaded_tokenizer([text], return_tensors="pt").to(DEVICE)
    streamer = TextIteratorStreamer(
        loaded_tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    # =========================================================
    # ⚡ 优化 2: 生成参数优化（关键！）
    # =========================================================
    generation_kwargs = dict(
        inputs,
        streamer=streamer,
        max_new_tokens=2048,  # ✅ 从 1024 降到 512（减少生成时间）
        do_sample=True,  #
        temperature=0.7,
        top_p=0.8,  # ✅ 从 0.9 降到 0.8（减少采样范围）
        top_k=40,  # ✅ 添加 top_k 限制
        repetition_penalty=1.1,  # ✅ 避免重复
        pad_token_id=loaded_tokenizer.eos_token_id,
        use_cache=True,  # ✅ 启用 KV cache
    )

    # 启动生成线程
    thread = Thread(target=loaded_model.generate, kwargs=generation_kwargs)
    thread.start()

    # =========================================================
    # ⚡ 优化 3: 流式输出优化（使用XML标记解析）
    # =========================================================
    # 预编译正则表达式
    thinking_start_pattern = re.compile(r"<thinking>")
    thinking_end_pattern = re.compile(r"</thinking>")
    answer_start_pattern = re.compile(r"<answer>")
    answer_end_pattern = re.compile(r"</answer>")

    current_type = "thinking"  # 当前状态：thinking/answer/none
    in_thinking = False
    in_answer = False
    full_content = ""
    buffer = ""  # 缓冲区，用于处理标记

    for new_text in streamer:
        full_content += new_text
        buffer += new_text

        # 检测<thinking>开始标记
        if not in_thinking and thinking_start_pattern.search(buffer):
            in_thinking = True
            current_type = "thinking"
            # 清除标记本身，不推送
            buffer = re.sub(r".*?<thinking>", "", buffer)
            continue

        # 检测</thinking>结束标记
        if in_thinking and thinking_end_pattern.search(buffer):
            in_thinking = False
            current_type = "none"
            # 清除标记本身
            buffer = re.sub(r"</thinking>.*", "", buffer)
            if buffer:
                yield {"token": buffer, "type": "thinking"}
            buffer = ""
            continue

        # 检测<answer>开始标记
        if not in_answer and answer_start_pattern.search(buffer):
            in_answer = True
            current_type = "answer"
            # 清除标记本身
            buffer = re.sub(r".*?<answer>", "", buffer)
            continue

        # 检测</answer>结束标记
        if in_answer and answer_end_pattern.search(buffer):
            in_answer = False
            current_type = "none"
            # 清除标记本身
            buffer = re.sub(r"</answer>.*", "", buffer)
            if buffer:
                yield {"token": buffer, "type": "answer"}
            buffer = ""
            continue

        # 推送正常内容
        if current_type in ["thinking", "answer"] and buffer:
            # 避免标记被拆分（等待下一个token确认）
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
