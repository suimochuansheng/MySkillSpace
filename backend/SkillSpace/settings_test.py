from .settings import *  # 继承主配置

# 覆盖数据库为内存 SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 可选：关闭 DEBUG 提升速度
DEBUG = False

# 可选：禁用密码哈希加密（加速用户创建）
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]