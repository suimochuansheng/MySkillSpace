# auth_system/signals.py
"""
用户信号处理器
自动为新创建的用户分配默认角色
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Role, User


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """
    当用户创建后，自动分配默认角色

    Args:
        sender: User模型类
        instance: 新创建的用户实例
        created: 是否是新创建（True）还是更新（False）
    """
    if created:  # 只处理新创建的用户
        # 检查用户是否已经有角色
        if instance.roles.count() == 0:
            try:
                # 尝试获取"普通用户"角色（优先级：normal > common > 第一个角色）
                default_role = Role.objects.filter(code="normal").first()

                # 如果没有normal角色，尝试common
                if not default_role:
                    default_role = Role.objects.filter(code="common").first()

                # 如果都没有，使用第一个可用角色
                if not default_role:
                    default_role = Role.objects.first()

                # 分配角色
                if default_role:
                    instance.roles.add(default_role)
                    print(
                        f"✅ 自动为用户 {instance.email} 分配角色：{default_role.name}"
                    )
                else:
                    print(
                        f"⚠️  警告：系统中没有可用角色，用户 {instance.email} 未分配角色"
                    )

            except Exception as e:
                print(f"❌ 为用户 {instance.email} 分配默认角色失败：{e}")
