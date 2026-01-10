from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from .models import AITask, ChatRecord


@admin.register(AITask)
class AITaskAdmin(admin.ModelAdmin):
    """AI 任务管理"""

    list_display = [
        "task_id_short",
        "user_display",
        "prompt_short",
        "status",
        "created_at",
        "completed_at",
    ]
    list_filter = ["status", "created_at", "user"]
    search_fields = ["task_id", "celery_task_id", "prompt", "user__username"]
    readonly_fields = ["task_id", "celery_task_id", "created_at"]
    ordering = ["-created_at"]

    fieldsets = (
        ("任务信息", {"fields": ("task_id", "celery_task_id", "status", "ws_url")}),
        ("用户信息", {"fields": ("user", "session_id")}),
        ("提问内容", {"fields": ("prompt",)}),
        ("时间信息", {"fields": ("created_at", "completed_at")}),
        ("错误信息", {"fields": ("error_message",), "classes": ("collapse",)}),
    )

    def task_id_short(self, obj):
        """显示简短的 task_id"""
        return f"{obj.task_id[:8]}..."

    task_id_short.short_description = "Task ID"

    def user_display(self, obj):
        """显示用户名"""
        return obj.user.username if obj.user else "匿名"

    user_display.short_description = "用户"

    def prompt_short(self, obj):
        """显示简短的提问"""
        return obj.prompt[:50] + "..." if len(obj.prompt) > 50 else obj.prompt

    prompt_short.short_description = "提问"


@admin.register(ChatRecord)
class ChatRecordAdmin(admin.ModelAdmin):
    """对话记录管理"""

    list_display = [
        "id",
        "session_id_short",
        "user_display",
        "role",
        "content_short",
        "created_at",
        "toggle_hidden_button",
    ]
    list_filter = ["role", "is_hidden", "created_at", "user"]
    search_fields = ["session_id", "content", "user__username"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    # 在详情页显示隐藏状态
    fieldsets = (
        ("基本信息", {"fields": ("session_id", "user", "role")}),
        ("对话内容", {"fields": ("content",)}),
        ("状态信息", {"fields": ("is_hidden", "created_at")}),
    )

    def session_id_short(self, obj):
        """显示简短的 session_id"""
        return f"{obj.session_id[:12]}..."

    session_id_short.short_description = "Session"

    def user_display(self, obj):
        """显示具体的用户账号信息"""
        if obj.user:
            # 显示：用户名 (ID: xxx)
            return format_html(
                '<span style="color: #007bff; font-weight: 500;">{}</span> '
                '<span style="color: #6c757d; font-size: 0.9em;">(ID: {})</span>',
                obj.user.username,
                obj.user.id,
            )
        else:
            # 未登录用户显示为红色
            return format_html('<span style="color: #dc3545; font-style: italic;">未登录</span>')

    user_display.short_description = "用户账号"

    def content_short(self, obj):
        """显示简短的内容"""
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content

    content_short.short_description = "内容"

    def toggle_hidden_button(self, obj):
        """显示隐藏/显示切换按钮"""
        if obj.is_hidden:
            # 当前已隐藏，显示"显示"按钮
            button_text = "👁️ 显示"
            button_color = "#28a745"  # 绿色
        else:
            # 当前可见，显示"隐藏"按钮
            button_text = "🙈 隐藏"
            button_color = "#ffc107"  # 黄色

        # 使用 ModelAdmin 的自定义 URL
        url = reverse("admin:ai_demo_chatrecord_toggle_hidden", args=[obj.pk])

        return format_html(
            '<a href="{}" style="'
            "background-color: {}; "
            "color: white; "
            "padding: 5px 12px; "
            "text-decoration: none; "
            "border-radius: 4px; "
            "font-size: 12px; "
            "font-weight: 600; "
            "display: inline-block; "
            'transition: all 0.2s;"'
            "onmouseover=\"this.style.opacity='0.8'\" "
            "onmouseout=\"this.style.opacity='1'\""
            ">{}</a>",
            url,
            button_color,
            button_text,
        )

    toggle_hidden_button.short_description = "操作"

    # 添加批量操作
    actions = ["hide_selected", "show_selected"]

    def hide_selected(self, request, queryset):
        """批量隐藏选中的记录"""
        updated = queryset.update(is_hidden=True)
        self.message_user(request, f"成功隐藏 {updated} 条记录")

    hide_selected.short_description = "隐藏选中的记录"

    def show_selected(self, request, queryset):
        """批量显示选中的记录"""
        updated = queryset.update(is_hidden=False)
        self.message_user(request, f"成功显示 {updated} 条记录")

    show_selected.short_description = "显示选中的记录"

    # 自定义 URL 路由
    def get_urls(self):
        """添加自定义 URL"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/toggle-hidden/",
                self.admin_site.admin_view(self.toggle_hidden_view),
                name="ai_demo_chatrecord_toggle_hidden",
            ),
        ]
        return custom_urls + urls

    def toggle_hidden_view(self, request, pk):
        """切换隐藏状态的视图"""
        try:
            chat_record = ChatRecord.objects.get(pk=pk)
            chat_record.is_hidden = not chat_record.is_hidden
            chat_record.save()

            if chat_record.is_hidden:
                messages.success(request, f"对话记录 #{pk} 已隐藏")
            else:
                messages.success(request, f"对话记录 #{pk} 已显示")

        except ChatRecord.DoesNotExist:
            messages.error(request, f"对话记录 #{pk} 不存在")

        # 重定向回列表页
        return HttpResponseRedirect(reverse("admin:ai_demo_chatrecord_changelist"))
