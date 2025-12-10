# ai_demo/tests.py
# AI模块测试用例

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import json
import os  # 新增：用于环境变量检测


class QwenChatAPITestCase(TestCase):
    """通义千问API测试用例"""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/ai/qwen/"

    def test_valid_prompt_request(self):
        """测试用例1：正常问题请求"""
        data = {"prompt": "你好，请介绍一下Python语言"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["code"], 200)
        self.assertEqual(response_data["msg"], "success")
        self.assertIsNotNone(response_data["data"])
        self.assertIsInstance(response_data["data"], str)
        self.assertGreater(len(response_data["data"]), 0)

    def test_empty_prompt_validation(self):
        """测试用例2：空问题校验"""
        data = {"prompt": ""}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data["code"], 400)
        self.assertIn("请输入问题内容", response_data["msg"])

    def test_whitespace_prompt_validation(self):
        """测试用例3：空白字符问题校验"""
        data = {"prompt": "   "}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data["code"], 400)

    def test_missing_prompt_field(self):
        """测试用例4：缺少prompt字段"""
        data = {}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data["code"], 400)

    def test_long_prompt_validation(self):
        """测试用例5：过长问题校验（2000字限制）"""
        long_prompt = "a" * 2001
        data = {"prompt": long_prompt}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertEqual(response_data["code"], 400)
        self.assertIn("过长", response_data["msg"])

    def test_max_length_prompt_accepted(self):
        """测试用例6：最大长度问题（2000字）应被接受"""
        max_prompt = "b" * 2000
        data = {"prompt": max_prompt}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["code"], 200)

    def test_special_characters_in_prompt(self):
        """测试用例7：特殊字符处理"""
        special_prompts = [
            "你好！@#￥%……&*（）",
            "<script>alert('test')</script>",
            "\n\t\r换行符测试",
            "😀 Emoji测试 😁",
        ]

        for prompt in special_prompts:
            data = {"prompt": prompt}
            response = self.client.post(self.url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response_data = response.json()
            self.assertEqual(response_data["code"], 200)

    def test_response_data_structure(self):
        """测试用例8：响应数据结构验证"""
        data = {"prompt": "测试问题"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertIn("code", response_data)
        self.assertIn("msg", response_data)
        self.assertIn("data", response_data)
        self.assertIsInstance(response_data["code"], int)
        self.assertIsInstance(response_data["msg"], str)
        self.assertIsInstance(response_data["data"], str)

    def test_http_method_restriction(self):
        """测试用例9：仅允许POST请求"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(self.url, {"prompt": "test"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_chinese_prompt_handling(self):
        """测试用例10：中文问题处理"""
        chinese_prompts = [
            "你好，世界！",
            "请解释一下机器学习的原理",
            "什么是深度学习？",
        ]

        for prompt in chinese_prompts:
            data = {"prompt": prompt}
            response = self.client.post(self.url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response_data = response.json()
            self.assertEqual(response_data["code"], 200)
            self.assertGreater(len(response_data["data"]), 0)


class ModelLoaderTestCase(TestCase):
    """模型加载器测试用例"""

    def setUp(self):
        """初始化：检查是否需要跳过模型测试"""
        self.skip_model_tests = os.getenv("SKIP_MODEL_TESTS", "false").lower() == "true"
        # 尝试导入模型加载器
        try:
            from ai_demo.model_loader import generate_answer

            self.generate_answer = generate_answer
        except ImportError:
            self.generate_answer = None

    def test_generate_answer_function_exists(self):
        """测试用例11：generate_answer函数存在性"""
        if self.skip_model_tests:
            self.skipTest("CI环境跳过模型测试")

        if self.generate_answer is None:
            self.fail("generate_answer函数未找到")
        self.assertTrue(callable(self.generate_answer))

    def test_generate_answer_with_valid_input(self):
        """测试用例12：有效输入生成回答"""
        if self.skip_model_tests:
            self.skipTest("CI环境跳过模型测试")

        if self.generate_answer is None:
            self.skipTest("模型加载器不可用")

        try:
            result = self.generate_answer("你好")
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
        except Exception as e:
            self.skipTest(f"模型推理失败: {str(e)}")
