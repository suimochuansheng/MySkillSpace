from django.urls import path

from .views import TriggerTaskView

urlpatterns = [
    path("trigger/", TriggerTaskView.as_view(), name="trigger_task"),
]
