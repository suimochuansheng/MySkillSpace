# ai_chat/model_loader.py
import torch
import bitsandbytes as bnb
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    BitsAndBytesConfig
)
from modelscope import snapshot_download
from threading import Lock
import traceback  # 移至顶部统一导入

model_lock = Lock()

# --------------------------
# 模型配置
# --------------------------
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
MODEL_CACHE_DIR = "./qwen_model_cache"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
MAX_PROMPT_LENGTH = 2000  # 与API限制保持一致

print(f"当前运行环境：torch={torch.__version__} | bitsandbytes={bnb.__version__} | CUDA={torch.version.cuda}")

# 下载模型
model_dir = snapshot_download(
    MODEL_NAME,
    cache_dir=MODEL_CACHE_DIR,
    revision="master"
)

# 加载tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    model_dir,
    trust_remote_code=True,
    padding_side="right",  # 确保padding在右侧
    use_fast=False
)

# --------------------------
# 量化配置
# --------------------------
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float32,  # 使用FP32避免溢出
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

print("正在加载模型 (FP32 Compute Mode)...")
model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    device_map=DEVICE,
    trust_remote_code=True,
    quantization_config=bnb_config
).eval()

# --------------------------
# 核心修改点 1: 修改系统提示词，加入思考过程指令
# --------------------------
SYSTEM_PROMPT = """你是一个乐于助人的AI助手。
请在回答问题之前，先进行深度的思维链分析。
请务必将你的思考过程包裹在 <think> 和 </think> XML标签中，然后再输出最终的回答。
例如：
<think>
这里需要分析用户的意图...
第一步是...
</think>
这里是正式的回答内容。
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

    with model_lock:
        try:
            # --------------------------
            # 核心修改点 2: 构建包含历史记录的消息列表
            # --------------------------
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # 追加历史记录 (限制最近 10 轮，防止显存爆满)
            # 假设 history 格式为 Django QuerySet 或 字典列表
            for msg in history[-10:]: 
                # 确保 role 是 model 识别的 user/assistant
                role = "user" if msg.get('role') == "user" else "assistant"
                messages.append({"role": role, "content": msg.get('content')})

            # 追加当前问题
            messages.append({"role": "user", "content": prompt})
            
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # 编码输入
            encoding = tokenizer([text], return_tensors="pt")
            input_ids = encoding.input_ids.to(DEVICE)
            attention_mask = encoding.attention_mask.to(DEVICE)
            
            # 生成配置
            generated_ids = model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_new_tokens=1024, # 增加长度以容纳思考过程
                do_sample=True,
                temperature=0.7,     # 稍微提高温度以增加思维多样性
                top_p=0.9,
                repetition_penalty=1.05,
                pad_token_id=tokenizer.eos_token_id
            )
            
            # 解码输出
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(input_ids, generated_ids)
            ]
            answer = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return answer
        
        except Exception as e:
            traceback.print_exc()
            return f"生成出错：{str(e)}"
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()