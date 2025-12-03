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

model_lock = Lock()

# --------------------------
# 模型配置
# --------------------------
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
MODEL_CACHE_DIR = "./qwen_model_cache"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

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
    padding_side="right", # 确保padding在右侧
    use_fast=False
)

# --------------------------
# 关键修改 1：使用 float32 进行计算
# --------------------------
# 解释：虽然模型权重存储为4-bit（很小），但我们将计算过程强制转为32位浮点数。
# 这会稍微增加一点点推理时的显存占用（约0.5GB），但能彻底解决 inf/nan 报错。
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float32, # ✅ 救命稻草：强制使用 FP32 避免溢出
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

def generate_answer(prompt: str) -> str:
    if not prompt.strip():
        return "请输入有效的问题！"
    
    with model_lock:
        try:
            # 1. 构建 Prompt
            messages = [
                {"role": "system", "content": "你是一个乐于助人的AI助手。"},
                {"role": "user", "content": prompt}
            ]
            
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # 2. 获取输入和 Attention Mask
            encoding = tokenizer([text], return_tensors="pt")
            input_ids = encoding.input_ids.to(DEVICE)
            attention_mask = encoding.attention_mask.to(DEVICE) # ✅ 显式获取 mask
            
            # 3. 生成配置 (保守参数，追求稳定)
            generated_ids = model.generate(
                input_ids,
                attention_mask=attention_mask, # ✅ 显式传入 mask，防止计算错误
                max_new_tokens=512,
                do_sample=True,
                temperature=0.6,    # 稍微降低温度，减少随机性带来的溢出风险
                top_p=0.9,
                repetition_penalty=1.05, # 稍微降低惩罚力度
                pad_token_id=tokenizer.eos_token_id
            )
            
            # 4. 解码
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(input_ids, generated_ids)
            ]
            answer = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return answer
        
        except Exception as e:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            import traceback
            traceback.print_exc()
            return f"生成出错：{str(e)}"