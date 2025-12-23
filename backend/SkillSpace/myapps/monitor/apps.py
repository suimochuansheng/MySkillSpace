from django.apps import AppConfig


class MonitorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitor"
    verbose_name = "系统监控"

    def ready(self):
        """应用启动时执行"""
        import os

        # 只在主进程中启动监控任务（避免 runserver 的自动重载导致重复启动）
        if os.environ.get("RUN_MAIN") == "true":
            from .tasks import get_monitor_task

            monitor_task = get_monitor_task()
            monitor_task.start()
