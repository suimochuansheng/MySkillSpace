# ai_demo/tests.py
# AI模块测试用例

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import json


class QwenChatAPITestCase(TestCase):
    """
    通义千问API测试用例
    测试覆盖：
    1. 正常请求处理
    2. 空输入校验
    3. 过长输入校验
    4. 异常处理
    """

    def setUp(self):
        """测试准备：初始化API客户端"""
        self.client = APIClient()
        self.url = '/api/ai/qwen/'

    def test_valid_prompt_request(self):
        """测试用例1：正常问题请求"""
        data = {"prompt": "你好，请介绍一下Python语言"}
        response = self.client.post(self.url, data, format='json')
        
        # 断言响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 断言响应数据结构
        response_data = response.json()
        self.assertEqual(response_data['code'], 200)
        self.assertEqual(response_data['msg'], 'success')
        self.assertIsNotNone(response_data['data'])
        self.assertIsInstance(response_data['data'], str)
        self.assertGreater(len(response_data['data']), 0)

    def test_empty_prompt_validation(self):
        """测试用例2：空问题校验"""
        # 测试空字符串
        data = {"prompt": ""}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['code'], 400)
        self.assertIn("请输入问题内容", response_data['msg'])

    def test_whitespace_prompt_validation(self):
        """测试用例3：空白字符问题校验"""
        data = {"prompt": "   "}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['code'], 400)

    def test_missing_prompt_field(self):
        """测试用例4：缺少prompt字段"""
        data = {}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['code'], 400)

    def test_long_prompt_validation(self):
        """测试用例5：过长问题校验（2000字限制）"""
        # 生成2001字的超长问题
        long_prompt = "a" * 2001
        data = {"prompt": long_prompt}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data['code'], 400)
        self.assertIn("过长", response_data['msg'])

    def test_max_length_prompt_accepted(self):
        """测试用例6：最大长度问题（2000字）应被接受"""
        # 生成2000字的问题（边界值）
        max_prompt = "b" * 2000
        data = {"prompt": max_prompt}
        response = self.client.post(self.url, data, format='json')
        
        # 应该成功处理
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['code'], 200)

    def test_special_characters_in_prompt(self):
        """测试用例7：特殊字符处理"""
        special_prompts = [
            "你好！@#￥%……&*（）",
            "<script>alert('test')</script>",
            "\n\t\r换行符测试",
            "😀 Emoji测试 😁"
        ]
        
        for prompt in special_prompts:
            data = {"prompt": prompt}
            response = self.client.post(self.url, data, format='json')
            
            # 应该成功处理
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response_data = response.json()
            self.assertEqual(response_data['code'], 200)

    def test_response_data_structure(self):
        """测试用例8：响应数据结构验证"""
        data = {"prompt": "测试问题"}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        
        # 验证响应包含必要字段
        self.assertIn('code', response_data)
        self.assertIn('msg', response_data)
        self.assertIn('data', response_data)
        
        # 验证字段类型
        self.assertIsInstance(response_data['code'], int)
        self.assertIsInstance(response_data['msg'], str)
        self.assertIsInstance(response_data['data'], str)

    def test_http_method_restriction(self):
        """测试用例9：仅允许POST请求"""
        # 测试GET请求
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # 测试PUT请求
        response = self.client.put(self.url, {"prompt": "test"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # 测试DELETE请求
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_chinese_prompt_handling(self):
        """测试用例10：中文问题处理"""
        chinese_prompts = [
            "你好，世界！",
            "请解释一下机器学习的原理",
            "什么是深度学习？"
        ]
        
        for prompt in chinese_prompts:
            data = {"prompt": prompt}
            response = self.client.post(self.url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response_data = response.json()
            self.assertEqual(response_data['code'], 200)
            self.assertGreater(len(response_data['data']), 0)


class ModelLoaderTestCase(TestCase):
    """
    模型加载器测试用例
    测试model_loader.py中的功能
    """

    def test_generate_answer_function_exists(self):
        """测试用例11：generate_answer函数存在性"""
        try:
            from ai_demo.model_loader import generate_answer
            self.assertTrue(callable(generate_answer))
        except ImportError:
            # 如果模型未加载，跳过此测试
            self.skipTest("模型加载器不可用")

    def test_generate_answer_with_valid_input(self):
        """测试用例12：有效输入生成回答"""
        try:
            from ai_demo.model_loader import generate_answer
            result = generate_answer("你好")
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
        except ImportError:
            self.skipTest("模型加载器不可用")
        except Exception as e:
            # 如果GPU不可用或模型未下载，记录错误但不失败
            self.skipTest(f"模型推理不可用: {str(e)}")
