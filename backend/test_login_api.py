"""
测试登录API - 诊断400错误
"""
import requests
import json

# 测试配置
BASE_URL = "http://localhost:9000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"

# 测试数据
test_cases = [
    {
        "name": "测试1: 正常登录请求（邮箱）",
        "data": {
            "account": "admin@example.com",  # 替换为你创建的用户邮箱
            "password": "admin123"  # 替换为实际密码
        }
    },
    {
        "name": "测试2: 正常登录请求（用户名）",
        "data": {
            "account": "admin",  # 替换为你创建的用户名
            "password": "admin123"  # 替换为实际密码
        }
    },
    {
        "name": "测试3: 缺少account字段",
        "data": {
            "password": "test123"
        }
    },
    {
        "name": "测试4: 缺少password字段",
        "data": {
            "account": "test@example.com"
        }
    },
    {
        "name": "测试5: 空数据",
        "data": {}
    }
]

def test_login(test_case):
    print(f"\n{'='*60}")
    print(f"🧪 {test_case['name']}")
    print(f"{'='*60}")
    print(f"📤 请求数据: {json.dumps(test_case['data'], indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            LOGIN_URL,
            json=test_case['data'],
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📥 响应状态码: {response.status_code}")
        print(f"📥 响应头: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📥 响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"📥 响应文本: {response.text}")
        
        if response.status_code == 200:
            print("✅ 测试通过")
        elif response.status_code == 400:
            print("❌ 400 Bad Request - 请求数据验证失败")
        else:
            print(f"⚠️ 未预期的状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    print("="*60)
    print("🔍 Django登录API诊断工具")
    print("="*60)
    print(f"📍 测试地址: {LOGIN_URL}")
    print(f"📍 后端服务: {BASE_URL}")
    
    for test_case in test_cases:
        test_login(test_case)
    
    print(f"\n{'='*60}")
    print("📊 测试完成")
    print("="*60)
    print("\n💡 诊断建议:")
    print("1. 如果所有测试都返回连接错误，检查Django服务是否运行")
    print("2. 如果测试1和2返回400，检查用户是否存在于数据库")
    print("3. 如果测试1和2返回200，说明后端API正常，问题在前端")
    print("4. 检查admin创建的用户是否设置了密码（需要使用set_password）")
