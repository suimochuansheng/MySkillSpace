import random
import time

from django.conf import settings
from django.core.mail import send_mail

from celery import shared_task

from .models import AsyncTask


@shared_task(bind=True)  # bind=True可访问任务实例，获取和操作具体实例的数据
def process_uploaded_file(self, file_name):
    """模拟文件处理（如压缩/转码）"""
    try:
        # 模拟耗时操作--后续可替换为实际文件处理逻辑
        time.sleep(3)
        result = f"Processed_{file_name}"

        # bind=True时才可进行以下同类型操作 更新数据库状态（可选）
        task = AsyncTask.objects.get(task_id=self.request.id)
        task.status = "success"
        task.save()

        return {"status": "success", "result": result}
    except Exception as e:
        task = AsyncTask.objects.get(task_id=self.request.id)
        task.status = "failed"
        task.save()
        raise e


@shared_task(bind=True)
def fetch_realtime_data(self, source):
    """模拟实时数据采集"""
    try:
        time.sleep(2)  # 模拟耗时操作--后续可替换为实际数据采集逻辑
        fake_data = {
            "source": source,
            "values": [random.randint(1, 100) for _ in range(5)],
            "timestamp": time.time(),
        }

        task = AsyncTask.objects.get(task_id=self.request.id)
        task.status = "success"
        task.save()

        return {"status": "success", "data": fake_data}
    except Exception as e:
        task = AsyncTask.objects.get(task_id=self.request.id)
        task.status = "failed"
        task.save()
        raise e


@shared_task(bind=True)
def send_welcome_email(self, email):
    """发送欢迎邮件（控制台打印）"""
    try:
        send_mail(
            subject="Welcome to Async Tasks Demo!",
            message="Your async task system is working perfectly!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        task = AsyncTask.objects.get(task_id=self.request.id)
        task.status = "success"
        task.save()

        return {"status": "success", "email": email}
    except Exception as e:
        task = AsyncTask.objects.get(task_id=self.request.id)
        task.status = "failed"
        task.save()
        raise e
