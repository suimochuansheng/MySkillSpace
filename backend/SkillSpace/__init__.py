import pymysql

# 让 Django 把 PyMySQL 当作 MySQLdb 来使用（关键）
pymysql.install_as_MySQLdb()

# 可选：解决某些环境下的版本警告（若出现警告再添加）
# pymysql.version_info = (1, 4, 6, 'final', 0)  # 模拟 mysqlclient 的版本号

# 导入 Celery 应用实例
from .celery_demo import app as celery_app

__all__ = ("celery_app",)
