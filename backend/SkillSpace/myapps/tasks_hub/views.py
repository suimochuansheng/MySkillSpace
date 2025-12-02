from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .tasks import process_uploaded_file, send_welcome_email, fetch_realtime_data
from .models import AsyncTask
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')  # csrf_exempt 装饰器免除了对CSRF令牌的验证
class TriggerTaskView(View):
    def post(self, request):
        # 解析请求体中的JSON数据，获取task_type参数，用于决定执行哪种异步任务
        data = json.loads(request.body)
        task_type = data.get('task_type')
        
        if task_type == 'file':
            file_name = data.get('file_name', 'test.jpg')
            task = process_uploaded_file.delay(file_name)
        elif task_type == 'data':
            source = data.get('source', 'stock_api')
            task = fetch_realtime_data.delay(source)
        elif task_type == 'email':
            email = data.get('email', 'test@example.com')
            task = send_welcome_email.delay(email)
        else:
            return JsonResponse({'error': 'Invalid task_type'}, status=400)
        
        # 保存任务记录到数据库
        AsyncTask.objects.create(
            task_id=task.id,
            task_type=task_type
        )
        
        return JsonResponse({
            'task_id': task.id,
            'status': 'Task started',
            'check_status_url': f'/tasks/status/{task.id}/'
        })