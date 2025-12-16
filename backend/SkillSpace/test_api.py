import requests
import json

# 注意：请确认你的端口是 8000 还是 9000
url = "http://localhost:9000/api/ai/qwen-async/"

payload = {
    "prompt": "介绍一下Python",
    "session_id": "test-001"
}

headers = {
    "Content-Type": "application/json"
}

try:
    print(f"正在发送请求到: {url} ...")
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"状态码: {response.status_code}")
    print("响应内容:")
    
    # 如果是流式响应，打印前几行看看
    if response.headers.get('content-type') == 'text/event-stream':
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
    else:
        print(response.text)

except Exception as e:
    print(f"请求失败: {e}")