"""
操作日志工具函数
用于记录用户操作和登录行为
"""

import json
import logging
import os
import time
from functools import wraps

import requests

# ==========================================
# 工具函数：获取请求信息
# ==========================================


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def parse_user_agent(user_agent_string):
    """
    解析User-Agent字符串
    简化版实现，返回浏览器和操作系统信息
    """
    if not user_agent_string:
        return {"browser": "Unknown", "os": "Unknown", "device": "Unknown"}

    ua_lower = user_agent_string.lower()

    # 浏览器检测
    if "edg" in ua_lower:
        browser = "Edge"
    elif "chrome" in ua_lower:
        browser = "Chrome"
    elif "firefox" in ua_lower:
        browser = "Firefox"
    elif "safari" in ua_lower:
        browser = "Safari"
    elif "opera" in ua_lower or "opr" in ua_lower:
        browser = "Opera"
    else:
        browser = "Other"

    # 操作系统检测
    if "windows" in ua_lower:
        os = "Windows"
    elif "mac" in ua_lower:
        os = "macOS"
    elif "linux" in ua_lower:
        os = "Linux"
    elif "android" in ua_lower:
        os = "Android"
    elif "ios" in ua_lower or "iphone" in ua_lower or "ipad" in ua_lower:
        os = "iOS"
    else:
        os = "Other"

    # 设备类型检测
    if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
        device = "Mobile"
    elif "tablet" in ua_lower or "ipad" in ua_lower:
        device = "Tablet"
    else:
        device = "Desktop"

    return {"browser": browser, "os": os, "device": device}


def get_ip_location(ip_address):
    """
    根据IP地址查询地理位置

    Args:
        ip_address: IP地址（支持IPv4和IPv6）

    Returns:
        地理位置字符串，如 "中国 广东省 深圳市" 或 "内网IP"
    """
    # 内网IP不查询
    if not ip_address or ip_address in ["127.0.0.1", "localhost", "::1"]:
        return "本地"

    # 内网IP段判断
    if ip_address.startswith(("10.", "172.", "192.168.")):
        return "内网IP"

    try:
        # 使用 ip-api.com 免费API（支持中文）
        # 免费限制：每分钟45次请求
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}",
            params={"lang": "zh-CN"},  # 返回中文地理位置
            timeout=3,  # 3秒超时
        )

        if response.status_code == 200:
            data = response.json()

            # API返回格式：
            # {
            #   "status": "success",
            #   "country": "中国",
            #   "regionName": "广东省",
            #   "city": "深圳市",
            #   ...
            # }

            if data.get("status") == "success":
                country = data.get("country", "")
                region = data.get("regionName", "")
                city = data.get("city", "")

                # 组合地理位置
                parts = [p for p in [country, region, city] if p]
                return " ".join(parts) if parts else "未知"

        # 如果失败，返回IP地址
        return f"未知({ip_address})"

    except requests.exceptions.Timeout:
        # 超时返回IP
        return f"查询超时({ip_address})"
    except Exception as e:
        # 查询失败，返回IP地址
        print(f"IP定位查询失败: {e}")
        return f"未知({ip_address})"


def get_request_params(request):
    """
    获取请求参数（GET/POST/JSON）
    """
    params = {}

    # GET参数
    if request.GET:
        params["GET"] = dict(request.GET)

    # POST参数
    if request.POST:
        params["POST"] = dict(request.POST)

    # JSON参数
    if hasattr(request, "data") and request.data:
        # 过滤敏感信息
        data = {
            k: ("******" if k in ["password", "old_password", "new_password", "password_confirm"] else v)
            for k, v in dict(request.data).items()
        }
        params["JSON"] = data

    return json.dumps(params, ensure_ascii=False) if params else ""


def get_module_name(path):
    """
    根据URL路径提取模块名
    """
    if "/auth/users" in path:
        return "用户管理"
    elif "/auth/roles" in path:
        return "角色管理"
    elif "/auth/menus" in path:
        return "菜单管理"
    elif "/resume" in path:
        return "简历管理"
    elif "/ai" in path:
        return "AI模块"
    else:
        return "其他"


def get_action_name(method, path):
    """
    根据HTTP方法和路径推断操作类型
    """
    if method == "GET":
        return "查询"
    elif method == "POST":
        if "login" in path:
            return "登录"
        elif "logout" in path:
            return "登出"
        else:
            return "新增"
    elif method in ["PUT", "PATCH"]:
        return "修改"
    elif method == "DELETE":
        return "删除"
    else:
        return "其他"


# ==========================================
# 记录操作日志的函数
# ==========================================


def record_operation_log(request, response, start_time, error=None):
    """
    记录操作日志到数据库

    Args:
        request: Django request对象
        response: Django response对象
        start_time: 请求开始时间
        error: 异常对象（如果有）
    """
    from .models import OperationLog

    try:
        # 计算执行时长
        duration = int((time.time() - start_time) * 1000)  # 毫秒

        # 获取用户信息
        user = request.user if request.user.is_authenticated else None
        username = user.email if user else "匿名用户"

        # 获取请求信息
        ip = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        params = get_request_params(request)

        # 获取模块和操作
        module = get_module_name(request.path)
        action = get_action_name(request.method, request.path)

        # 获取响应数据（限制大小）
        response_data = ""
        if hasattr(response, "data"):
            response_str = json.dumps(response.data, ensure_ascii=False)
            response_data = response_str[:1000]  # 限制最多1000字符

        # 判断状态
        status = "1" if error or (hasattr(response, "status_code") and response.status_code >= 400) else "0"

        # 创建日志
        OperationLog.objects.create(
            user=user,
            username=username,
            module=module,
            action=action,
            description=f"{action} {module}",
            method=request.method,
            url=request.path,
            ip_address=ip,
            user_agent=user_agent[:255],  # 限制长度
            request_params=params,
            response_data=response_data,
            status=status,
            error_msg=str(error) if error else "",
            duration=duration,
        )
    except Exception as e:
        # 记录日志失败时，打印错误但不中断业务流程
        print(f"记录操作日志失败: {e}")


def record_login_log(request, username, status, msg=""):
    """
    记录登录日志

    Args:
        request: Django request对象
        username: 登录账号
        status: 登录状态 ('0'成功, '1'失败)
        msg: 提示信息
    """
    from .models import LoginLog

    try:
        ip = get_client_ip(request)
        user_agent_string = request.META.get("HTTP_USER_AGENT", "")
        ua_info = parse_user_agent(user_agent_string)

        # 查询IP地理位置
        location = get_ip_location(ip)

        LoginLog.objects.create(
            username=username,
            ip_address=ip,
            login_location=location,  # 填充地理位置
            browser=ua_info["browser"],
            os=ua_info["os"],
            device=ua_info["device"],
            status=status,
            msg=msg,
        )
    except Exception as e:
        print(f"记录登录日志失败: {e}")


def record_fail2ban_log(request, account):
    """
    记录登录失败日志到fail2ban专用日志文件
    用于fail2ban监控和封禁恶意IP

    Args:
        request: Django request对象
        account: 尝试登录的账号
    """
    try:
        # 获取客户端IP
        ip = get_client_ip(request)

        # 配置fail2ban专用日志记录器
        fail2ban_logger = logging.getLogger("fail2ban_login")

        # 如果logger还没有handler，配置一个
        if not fail2ban_logger.handlers:
            # 日志文件路径（Docker容器内路径）
            log_file = "/app/logs/login_fail.log"

            # 创建目录（如果不存在）
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            # 创建文件处理器
            handler = logging.FileHandler(log_file, encoding="utf-8")

            # 设置日志格式（fail2ban需要的格式）
            formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)

            # 添加处理器
            fail2ban_logger.addHandler(handler)
            fail2ban_logger.setLevel(logging.WARNING)

        # 记录登录失败（fail2ban会匹配这个格式）
        fail2ban_logger.warning(f"登录失败 - 账号: {account}, IP: {ip}")

    except Exception as e:
        # 记录失败不影响主流程
        print(f"记录fail2ban日志失败: {e}")


# ==========================================
# 装饰器：自动记录操作日志
# ==========================================


def log_operation(module=None, action=None, description=""):
    """
    操作日志装饰器 - 用于ViewSet的action或APIView

    用法：
        @log_operation(module='用户管理', action='删除', description='删除用户')
        @action(detail=True, methods=['post'])
        def delete_user(self, request, pk=None):
            ...

    或者对整个视图类使用：
        @method_decorator(log_operation(module='用户管理'), name='dispatch')
        class UserView(APIView):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request_or_self, *args, **kwargs):
            # 兼容类视图和函数视图
            if hasattr(request_or_self, "request"):
                # ViewSet的action，request_or_self是self
                request = request_or_self.request
            else:
                # 函数视图，request_or_self是request
                request = request_or_self

            start_time = time.time()
            error = None
            response = None

            try:
                # 执行视图函数
                response = view_func(request_or_self, *args, **kwargs)
                return response
            except Exception as e:
                error = e
                raise
            finally:
                # 记录日志（无论成功或失败）
                try:
                    record_operation_log(request, response, start_time, error)
                except Exception:  # noqa: E722
                    pass  # 日志记录失败不影响业务

        return wrapped_view

    return decorator
