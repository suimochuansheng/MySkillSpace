"""
操作日志工具函数
用于记录用户操作和登录行为
"""
import json
import time
from functools import wraps

from django.utils import timezone
from rest_framework.response import Response


# ==========================================
# 工具函数：获取请求信息
# ==========================================

def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_user_agent(user_agent_string):
    """
    解析User-Agent字符串
    简化版实现，返回浏览器和操作系统信息
    """
    if not user_agent_string:
        return {
            'browser': 'Unknown',
            'os': 'Unknown',
            'device': 'Unknown'
        }

    ua_lower = user_agent_string.lower()

    # 浏览器检测
    if 'edg' in ua_lower:
        browser = 'Edge'
    elif 'chrome' in ua_lower:
        browser = 'Chrome'
    elif 'firefox' in ua_lower:
        browser = 'Firefox'
    elif 'safari' in ua_lower:
        browser = 'Safari'
    elif 'opera' in ua_lower or 'opr' in ua_lower:
        browser = 'Opera'
    else:
        browser = 'Other'

    # 操作系统检测
    if 'windows' in ua_lower:
        os = 'Windows'
    elif 'mac' in ua_lower:
        os = 'macOS'
    elif 'linux' in ua_lower:
        os = 'Linux'
    elif 'android' in ua_lower:
        os = 'Android'
    elif 'ios' in ua_lower or 'iphone' in ua_lower or 'ipad' in ua_lower:
        os = 'iOS'
    else:
        os = 'Other'

    # 设备类型检测
    if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
        device = 'Mobile'
    elif 'tablet' in ua_lower or 'ipad' in ua_lower:
        device = 'Tablet'
    else:
        device = 'Desktop'

    return {
        'browser': browser,
        'os': os,
        'device': device
    }


def get_request_params(request):
    """
    获取请求参数（GET/POST/JSON）
    """
    params = {}

    # GET参数
    if request.GET:
        params['GET'] = dict(request.GET)

    # POST参数
    if request.POST:
        params['POST'] = dict(request.POST)

    # JSON参数
    if hasattr(request, 'data') and request.data:
        # 过滤敏感信息
        data = {
            k: '******' if k in ['password', 'old_password', 'new_password', 'password_confirm']
            else v
            for k, v in dict(request.data).items()
        }
        params['JSON'] = data

    return json.dumps(params, ensure_ascii=False) if params else ''


def get_module_name(path):
    """
    根据URL路径提取模块名
    """
    if '/auth/users' in path:
        return '用户管理'
    elif '/auth/roles' in path:
        return '角色管理'
    elif '/auth/menus' in path:
        return '菜单管理'
    elif '/resume' in path:
        return '简历管理'
    elif '/ai' in path:
        return 'AI模块'
    else:
        return '其他'


def get_action_name(method, path):
    """
    根据HTTP方法和路径推断操作类型
    """
    if method == 'GET':
        return '查询'
    elif method == 'POST':
        if 'login' in path:
            return '登录'
        elif 'logout' in path:
            return '登出'
        else:
            return '新增'
    elif method in ['PUT', 'PATCH']:
        return '修改'
    elif method == 'DELETE':
        return '删除'
    else:
        return '其他'


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
        username = user.email if user else '匿名用户'

        # 获取请求信息
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        params = get_request_params(request)

        # 获取模块和操作
        module = get_module_name(request.path)
        action = get_action_name(request.method, request.path)

        # 获取响应数据（限制大小）
        response_data = ''
        if hasattr(response, 'data'):
            response_str = json.dumps(response.data, ensure_ascii=False)
            response_data = response_str[:1000]  # 限制最多1000字符

        # 判断状态
        status = '1' if error or (hasattr(response, 'status_code') and response.status_code >= 400) else '0'

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
            error_msg=str(error) if error else '',
            duration=duration
        )
    except Exception as e:
        # 记录日志失败时，打印错误但不中断业务流程
        print(f"记录操作日志失败: {e}")


def record_login_log(request, username, status, msg=''):
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
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        ua_info = parse_user_agent(user_agent_string)

        LoginLog.objects.create(
            username=username,
            ip_address=ip,
            login_location='',  # 可以集成IP定位服务
            browser=ua_info['browser'],
            os=ua_info['os'],
            device=ua_info['device'],
            status=status,
            msg=msg
        )
    except Exception as e:
        print(f"记录登录日志失败: {e}")


# ==========================================
# 装饰器：自动记录操作日志
# ==========================================

def log_operation(module=None, action=None, description=''):
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
            if hasattr(request_or_self, 'request'):
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
                except:
                    pass  # 日志记录失败不影响业务

        return wrapped_view
    return decorator
