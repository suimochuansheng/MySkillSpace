# auth_system/signals.py
"""
用户信号处理器
自动为新创建的用户分配默认角色
"""
import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Role, User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """
    当用户创建后，自动分配默认角色
    如果系统中没有任何角色，则回滚用户创建并抛出异常

    Args:
        sender: User模型类
        instance: 新创建的用户实例
        created: 是否是新创建（True）还是更新（False）

    Raises:
        ValidationError: 当系统中没有可用角色时
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

                # 如果系统中没有任何角色，阻止用户创建
                if not default_role:
                    logger.error(f"❌ 无法创建用户 {instance.email}：系统中没有可用角色")

                    # 删除刚创建的用户
                    instance.delete()

                    # 抛出验证错误
                    raise ValidationError(
                        "无法创建用户：系统中没有可用的角色！\n"
                        "请先在【系统管理 → 角色管理】中创建至少一个角色，\n"
                        "然后再创建用户。"
                    )

                # 分配角色
                instance.roles.add(default_role)
                logger.info(f"✅ 自动为用户 {instance.email} 分配角色：{default_role.name}")

            except ValidationError:
                # 重新抛出ValidationError（不捕获，让上层处理）
                raise

            except Exception as e:
                logger.error(f"❌ 为用户 {instance.email} 分配默认角色失败：{e}")
                # 如果分配角色失败，也删除用户
                instance.delete()
                raise ValidationError(f"创建用户失败：{str(e)}")
