# 全局celery实例
import os  # <--- 必须导入 os
from celery import Celery

# 告诉 Celery Django 的配置文件在哪里
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkillSpace.settings')

# 配置celery
app = Celery("SkillSpace")
# 从django配置中加载celery配置
app.config_from_object("django.conf:settings", namespace="CELERY")
# 自动发现 tasks_hub.tasks
app.autodiscover_tasks()

# 从 kombu 导入 Queue 类：kombu 是 Celery 底层依赖的消息传输库，Queue 用于定义任务队列的结构和属性
from kombu import Queue

# 配置 Celery 任务队列（多队列分类，实现任务优先级和资源隔离）
app.conf.task_queues = (
    # 1. GPU 专属队列：处理依赖 GPU 的重量级任务（如 AI 推理、模型训练）
    Queue(
        name='gpu_queue',  # 队列名称（唯一标识）
        routing_key='gpu.#',  # 路由键：匹配任务的路由规则（# 是通配符，匹配 gpu. 开头的所有路由键）
        priority=9,  # 队列优先级：数值越大，Worker 越优先消费该队列的任务（范围需 ≤ 下面的 x-max-priority）
        queue_arguments={'x-max-priority': 10}  # RabbitMQ 扩展参数：设置队列支持的最大优先级（仅 RabbitMQ 支持该参数）
    ),
    # 2. API 业务队列：处理接口类任务（如简历解析、数据查询，耗时中等）
    Queue(
        name='api_queue',
        routing_key='api.#',  # 匹配 api. 开头的所有路由键
        priority=5,  # 优先级低于 GPU 队列，高于默认队列
        queue_arguments={'x-max-priority': 10}  # 统一最大优先级为 10，方便管理
    ),
    # 3. 默认队列：处理通用、低优先级任务（如日志同步、邮件发送，耗时短/非核心）
    Queue(
        name='default',
        routing_key='task.#',  # 匹配 task. 开头的所有路由键
        priority=3,  # 最低优先级
        queue_arguments={'x-max-priority': 10}
    ),
)

# 配置任务路由规则：指定「哪些任务」发送到「哪个队列」（实现任务分类分发）
app.conf.task_routes = {
    # 规则1：流式任务 → 路由到 gpu_queue
    'myapps.ai_demo.tasks.qwen_chat_task_streaming': {'queue': 'gpu_queue'},
    # 规则2：非流式任务 → 路由到 gpu_queue
    'myapps.ai_demo.tasks.qwen_chat_task': {'queue': 'gpu_queue'},
    # 规则3：通配符匹配（* 匹配 tasks 模块下所有任务）→ 路由到 api_queue
    'myapps.resume.tasks.*': {'queue': 'api_queue'},
    # 隐含规则：未匹配到的任务，会自动路由到「default」队列（Celery 默认行为）
}

# 并发控制配置：优化 Worker 执行效率，避免资源耗尽或内存泄漏
# 1. 预取任务数：Worker 每次从队列中预取的任务数量（默认是 4）
# 设为 1 表示「一次只处理一个任务」，适合 GPU 任务（GPU 通常单任务独占资源，避免多任务抢占）
app.conf.worker_prefetch_multiplier = 1

# 2.  Worker 最大任务数：每个 Worker 进程处理 N 个任务后自动重启（默认无限制）
# 设为 50 是为了防止长期运行导致的内存泄漏（如 AI 模型加载后内存不释放、第三方库缓存累积）
app.conf.worker_max_tasks_per_child = 50