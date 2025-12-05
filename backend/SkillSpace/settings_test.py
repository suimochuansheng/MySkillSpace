"""  
Django 测试环境配置
用于 CI/CD 和本地测试，使用 SQLite 内存数据库
"""

import os
import sys
from pathlib import Path

# 构建基础路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 添加 myapps 目录到 Python 路径
sys.path.insert(0, os.path.join(BASE_DIR, 'SkillSpace', 'myapps'))

# ========== 核心配置 ==========
SECRET_KEY = os.getenv('SECRET_KEY', 'test-secret-key-for-ci-only-do-not-use-in-production')
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# ========== 应用配置 ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方应用
    'rest_framework',
    'corsheaders',
    # myapps
    'tasks_hub',
    'resume',
    'auth_system',
]

# ========== 中间件配置 ==========
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========== CORS 配置 ==========
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:8080",
]
CORS_ALLOW_CREDENTIALS = True

# ========== URL 配置 ==========
ROOT_URLCONF = 'SkillSpace.urls'

# ========== 模板配置 ==========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SkillSpace.wsgi.application'

# ========== 数据库配置（SQLite 内存模式）==========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # 使用内存数据库，测试结束后自动清空
    }
}

# ========== 密码验证器 ==========
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========== 国际化配置 ==========
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# ========== REST Framework 配置 ==========
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

# ========== 静态文件配置 ==========
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========== Celery 配置（测试环境使用内存模式）==========
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'memory://')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'cache+memory://')
CELERY_TASK_ALWAYS_EAGER = True  # 同步执行任务，方便测试
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'

# ========== 邮件配置（测试环境使用控制台输出）==========
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@skillspace.local'

# ========== 默认主键字段类型 ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== 自定义用户模型 ==========
AUTH_USER_MODEL = 'auth_system.User'

# ========== 测试优化配置 ==========
# 禁用密码哈希加密（加速用户创庻）
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 禁用迁移检查加速测试
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

# 可选：禁用迁移检查（取消注释以启用）
# MIGRATION_MODULES = DisableMigrations()