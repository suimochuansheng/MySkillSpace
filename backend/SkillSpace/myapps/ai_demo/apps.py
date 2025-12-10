from django.apps import AppConfig
import threading


class AiDemoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_demo"

    def ready(self):
        """
        Django应用启动时调用
        在后台线程中加载AI模型，不阻塞服务启动
        """
        # 避免在runserver的重载监控进程中重复加载
        import os

        if os.environ.get("RUN_MAIN") != "true":
            return

        # 在后台线程中加载模型
        def load_model_async():
            try:
                from . import model_loader

                model_loader.load_model_on_startup()
            except Exception as e:
                print(f"❌ 模型加载线程异常：{e}")

        # 启动后台线程
        thread = threading.Thread(
            target=load_model_async, daemon=True, name="ModelLoader"
        )
        thread.start()
        print("🚀 AI模型加载线程已启动，服务将立即就绪")
