# 全局celery实例

from celery import Celery
# 配置celery
app = Celery('SkillSpace')
# 从django配置中加载celery配置
app.config_from_object('django.conf:settings', namespace='CELERY')
# 自动发现 tasks_hub.tasks
app.autodiscover_tasks()