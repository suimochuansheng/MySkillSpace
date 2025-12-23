"""
操作日志中间件 - 自动记录所有API请求的操作日志
Django ASGI中间件，用于拦截HTTP请求和响应
"""

import json
import logging
import time

from django.utils.deprecation import MiddlewareMixin

from .models import OperationLog

logger = logging.getLogger(__name__)


class OperationLogMiddleware(MiddlewareMixin):
    """
    操作日志记录中间件

    自动记录以下信息：
    - 请求方法、路径、参数
    - 响应状态码
    - 操作用户、IP地址
    - 执行耗时
    - 错误信息（如有）

    使用方式：
    在 settings.py 的 MIDDLEWARE 列表中添加：
    'auth_system.middleware.OperationLogMiddleware'
    """

    # 不需要记录的URL路径前缀（避免过度记录）
    EXCLUDE_PATHS = [
        "/admin/",
        "/static/",
        "/media/",
        "/api/auth/login/",  # 登录单独处理
        "/api/auth/register/",  # 注册单独处理
        "/api/auth/logout/",  # 登出单独处理
        # AI操作已恢复记录（使用request.data兼容DRF，避免request.body冲突）
    ]

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response

    def should_log(self, path, method):
        """
        判断是否应该记录此请求

        Args:
            path: 请求路径
            method: HTTP方法

        Returns:
            bool: True表示应该记录
        """
        # 只记录API请求（以/api/开头）
        if not path.startswith("/api/"):
            return False

        # 检查是否在排除列表中
        for exclude_path in self.EXCLUDE_PATHS:
            if path.startswith(exclude_path):
                return False

        # 只记录修改数据的请求（POST, PUT, DELETE, PATCH）
        if method not in ["POST", "PUT", "DELETE", "PATCH"]:
            return False

        return True

    def _parse_request_params(self, request):
        """
        解析请求参数（兼容DRF）
        """
        try:
            if request.method == "GET":
                return str(dict(request.GET))
            elif request.method in ["POST", "PUT", "PATCH"]:
                # ✅ 修复：优先使用DRF的request.data（如果可用）
                # 避免 "You cannot access body after reading from request's data stream" 错误
                if hasattr(request, "data"):
                    try:
                        # DRF的request.data已经解析好了，直接使用
                        return json.dumps(dict(request.data), ensure_ascii=False)
                    except Exception as e:
                        # 如果request.data不是dict，尝试其他方式
                        return str(request.data)[:500]
                # 如果不是DRF请求，尝试原生request.body
                elif request.content_type == "application/json":
                    try:
                        return json.dumps(json.loads(request.body), ensure_ascii=False)
                    except Exception:
                        return str(request.body)[:500]
                else:
                    return str(dict(request.POST))
            return ""
        except Exception as e:
            # ✅ 降级：出错时不影响主流程，仅记录警告
            logger.warning(f"解析请求参数失败（已忽略）: {e}")
            return ""

    def _parse_response_data(self, response):
        """
        解析响应数据
        """
        try:
            if hasattr(response, "content"):
                content = response.content
                if isinstance(content, bytes):
                    # 只记录JSON响应（前500字符）
                    try:
                        data = json.loads(content)
                        return json.dumps(data, ensure_ascii=False)[:500]
                    except Exception:
                        return ""
            return ""
        except Exception as e:
            logger.error(f"解析响应数据失败: {e}")
            return ""

    def _get_client_ip(self, request):
        """
        获取客户端IP地址
        """
        # 优先检查代理IP（Nginx等反向代理）
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def _get_user_agent_info(self, request):
        """
        提取用户代理信息
        """
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        # 简单解析（可以使用user-agents库做更精确的解析）
        return user_agent

    def _infer_module_and_action(self, request, path):
        """
        从请求路径推断操作模块和操作类型

        例如：
        - POST /api/auth/users/ -> module='用户管理', action='新增'
        - PUT /api/auth/users/1/ -> module='用户管理', action='修改'
        - DELETE /api/auth/users/1/ -> module='用户管理', action='删除'
        """
        method_map = {
            "POST": "新增",
            "PUT": "修改",
            "PATCH": "修改",
            "DELETE": "删除",
        }

        action = method_map.get(request.method, "其他")

        # 根据路径推断模块
        if "/auth/users/" in path:
            module = "用户管理"
        elif "/auth/roles/" in path:
            module = "角色管理"
        elif "/auth/menus/" in path:
            module = "菜单管理"
        elif "/resume/" in path:
            module = "简历管理"
        elif "/tasks/" in path:
            module = "任务管理"
        elif "/ai/" in path:
            module = "AI演示"
        else:
            module = "其他操作"

        return module, action

    def process_request(self, request):
        """
        请求前置处理
        记录请求开始时间
        """
        request._operation_log_start_time = time.time()
        return None

    def process_response(self, request, response):
        """
        响应后置处理
        记录操作日志
        """
        # 检查是否应该记录此请求
        if not self.should_log(request.path, request.method):
            return response

        try:
            # 计算执行耗时
            start_time = getattr(request, "_operation_log_start_time", None)
            if start_time:
                duration = int((time.time() - start_time) * 1000)  # 转换为毫秒
            else:
                duration = 0

            # 提取信息
            username = (
                request.user.username
                if request.user and request.user.is_authenticated
                else "未知用户"
            )
            ip_address = self._get_client_ip(request)
            method = request.method
            url = request.path
            user_agent = self._get_user_agent_info(request)
            request_params = self._parse_request_params(request)
            response_data = self._parse_response_data(response)
            status_code = response.status_code

            # 推断模块和操作类型
            module, action = self._infer_module_and_action(request, url)

            # 判断操作是否成功（状态码 2xx 表示成功）
            is_success = 200 <= status_code < 300
            status = "0" if is_success else "1"

            # 创建操作日志记录
            log = OperationLog.objects.create(
                user=(
                    request.user
                    if request.user and request.user.is_authenticated
                    else None
                ),
                username=username,
                module=module,
                action=action,
                description=f"{action}{module}",
                method=method,
                url=url,
                ip_address=ip_address,
                user_agent=user_agent,
                request_params=request_params,
                response_data=response_data,
                status=status,
                error_msg="" if is_success else f"状态码: {status_code}",
                duration=duration,
            )

            logger.info(
                f"[操作日志] {username} | {method} {url} | "
                f"模块: {module} | 操作: {action} | "
                f'结果: {"成功" if is_success else "失败"} | '
                f"耗时: {duration}ms"
            )

        except Exception as e:
            # 记录日志失败不应该影响正常的请求响应
            logger.error(f"[操作日志中间件] 记录失败: {e}", exc_info=True)

        return response
