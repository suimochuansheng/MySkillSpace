# SkillSpace - 技能分享与学习社区平台

<div align="center">
  <p>一个基于 Django + Vue3 的现代化前后端分离应用</p>
  <p>专注于技能分享、学习交流与个人成长</p>
</div>

---

## 📖 项目简介

**SkillSpace** 是一个功能完善的技能分享与学习社区平台，采用前后端分离架构，为用户提供便捷的技能交流和个人成长服务。

### 核心功能模块

- **🔐 用户认证系统（auth_system）**  
  基于自定义用户模型的完整认证体系，支持邮箱登录、用户注册、权限管理、菜单控制等功能

- **📝 简历管理（resume）**  
  个人简历在线编辑与管理，支持多维度技能展示、项目经历记录、AI智能诊断等

- **⚙️ 任务中心（tasks_hub）**  
  基于 Celery 的异步任务处理系统，支持邮件发送、报告生成、数据导出等耗时操作

- **🤖 AI演示（ai_demo）**  
  集成大语言模型的AI对话功能，支持智能问答、代码生成、文本分析等

- **📊 数据看板（Dashboard）**  
  可视化数据分析与展示，包含用户画像、任务统计、数据分析等模块

- **🔑 权限管理系统（sys）**  
  完整的RBAC权限管理体系，支持用户、角色、菜单的灵活配置

---

## 🔧 技术栈

### 后端技术

| 类别 | 技术 | 说明 |
|------|------|------|
| **核心框架** | Django 4.2.x | Python Web 框架 |
| **API框架** | Django REST Framework | RESTful API 构建 |
| **数据库** | SQLite / MySQL 8.0 | 开发/生产环境（SQLite用于开发） |
| **异步任务** | Celery 5.5.x | 分布式任务队列 |rabbitmq | 作为任务队列的中间件
| **消息队列** | Redis | Celery Broker 与结果后端 |
| **缓存** | Redis 6.2 | 缓存与会话存储 |
| **跨域处理** | django-cors-headers | CORS 跨域配置 |
| **后台美化** | django-simpleui | Admin 界面优化 |
| **数据库驱动** | PyMySQL | MySQL 连接器 |
| **环境管理** | python-dotenv | 环境变量管理 |

### 前端技术

| 类别 | 技术 | 说明 |
|------|------|------|
| **构建工具** | Vite 7.2.x | 新一代前端构建工具 |
| **核心框架** | Vue 3.5.x | 渐进式 JavaScript 框架 |
| **UI组件库** | Element Plus 2.11.x | 基于 Vue 3 的组件库 |
| **图标库** | @element-plus/icons-vue | Element Plus 图标集 |
| **HTTP客户端** | Fetch API | 原生HTTP客户端封装 |
| **状态管理** | Pinia（可选） | Vue 3 官方状态管理 |
| **开发语言** | JavaScript (ES6+) | 现代化 JavaScript |
| **路由管理** | Vue Router 4.x | Vue官方路由管理 |

### AI/机器学习（可选）

- **深度学习框架**: PyTorch 2.1.2  
- **模型库**: Transformers 4.36.2  
- **模型支持**: Qwen-7B-Chat 大语言模型  
- **加速库**: Accelerate、bitsandbytes  

---

## 📋 环境要求

### 运行时环境

- **Python**: ≥ 3.8（推荐 3.9+）
- **Node.js**: ≥ 16.x（推荐 18.x LTS）
- **数据库**: SQLite（开发）或 MySQL 8.0+（生产）
- **Redis**: ≥ 6.2（用于 Celery 和缓存）

### 包管理工具

- **后端**: pip（Python 包管理器）
- **前端**: npm / yarn / pnpm（推荐 npm）

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <你的仓库地址> skillSpace
cd skillSpace
```

### 2. 后端环境配置

#### 2.1 创建虚拟环境

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### 2.2 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 如需GPU支持（CUDA 11.8）
pip install torch==2.1.2+cu118 torchaudio==2.1.2+cu118 torchvision==0.16.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

#### 2.3 配置环境变量

在 `backend/` 目录下创建 `.env` 文件：

```env
# Django配置
SECRET_KEY=your-secret-key-here
DEBUG=True

# 数据库配置（SQLite用于开发，MySQL用于生产）
# SQLite配置（默认）
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# MySQL配置（生产环境）
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=skillspace
# DB_USER=root
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=3306

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### 2.4 初始化数据库

```bash
# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 初始化菜单数据（可选）
python manage.py init_menus
```

#### 2.5 启动后端服务

```bash
# 启动Django开发服务器
python manage.py runserver

# 访问地址：http://127.0.0.1:8000/
# Admin后台：http://127.0.0.1:8000/admin/
```

#### 2.6 启动Celery Worker（可选）

```bash
# 新终端窗口，确保虚拟环境已激活
celery -A SkillSpace worker --loglevel=info

# Windows用户可能需要
celery -A SkillSpace worker --loglevel=info --pool=solo
```

### 3. 前端环境配置

#### 3.1 安装依赖

```bash
cd frontend/skillspace
npm install
# 或使用 yarn/pnpm
# yarn install
# pnpm install
```

#### 3.2 启动开发服务器

```bash
npm run dev

# 访问地址：http://localhost:5173/
```

#### 3.3 构建生产版本

```bash
npm run build

# 预览构建结果
npm run preview
```

---

## 🛠️ VSCode 开发环境配置

### 一键启动调试

本项目已配置完整的 VSCode 调试环境，支持：

- ✅ Django 后端调试（支持断点、变量监视、调用堆栈）
- ✅ 单个 Python 文件独立运行和调试
- ✅ Celery 异步任务调试
- ✅ 前后端同时启动（全栈调试）
- ✅ Django 管理命令调试（migrate、makemigrations等）

### 快速开始

1. **打开工作区**
   ```bash
   code skillspace.code-workspace
   ```

2. **安装推荐扩展**
   - VSCode 会自动提示安装推荐扩展
   - 点击"安装所有"

3. **选择 Python 解释器**
   - 按 `Ctrl+Shift+P`
   - 输入 `Python: Select Interpreter`
   - 选择 `.venv\Scripts\python.exe`

4. **启动调试**
   - 按 `F5`
   - 选择 `Django: 启动后端服务器`
   - 开始调试！

### 调试配置说明

| 配置名称 | 快捷键 | 用途 |
|---------|--------|------|
| Django: 启动后端服务器 | F5 | 完整功能开发（启用AI） |
| Django: 启动后端服务器 (禁用AI) | F5 | 快速启动（禁用AI模型） |
| Python: 当前文件 | F5 | 运行当前Python文件 |
| 全栈调试: Django + 前端 | F5 | 同时启动前后端 |
| Celery: 启动Worker | F5 | 异步任务调试 |
| 测试: RabbitMQ连接 | F5 | 测试消息队列连接 |

### 常用任务

按 `Ctrl+Shift+P` → `Tasks: Run Task` 可执行以下任务：

- **前端: 启动开发服务器** - 启动 Vite 开发服务器
- **Django: 数据库迁移** - 执行数据库迁移
- **Docker: 启动所有服务** - 启动 MySQL/RabbitMQ/Redis
- **初始化: 完整项目设置** - 一键初始化项目环境

### 调试技巧

#### 设置断点
1. 点击代码行号左侧设置断点
2. 按 `F5` 启动调试
3. 触发断点（访问对应接口）
4. 使用调试控制台查看变量

#### 条件断点
右键断点 → 编辑断点 → 添加条件：
```python
user.username == "admin"
```

#### 日志断点
右键断点 → 编辑断点 → Logpoint：
```python
f"用户 {user.username} 正在登录"
```

### 详细文档

- [VSCode 配置详细文档](.vscode/README.md) - 660行完整指南
- [快速参考卡片](VSCODE_DEBUG_GUIDE.md) - 速查手册
- [配置总结](VSCODE_CONFIGURATION_SUMMARY.md) - 配置说明

### celery_test.py 运行说明

**问题**: 直接运行 `celery_test.py` 会报模块导入错误

**原因**: 项目中存在 `celery.py` 文件，导致模块命名冲突

**解决方案**: 使用 VSCode 调试配置
1. 按 `F5`
2. 选择 `测试: RabbitMQ连接`
3. 查看输出结果

---

## ⚙️ 配置说明

### CORS 跨域配置

项目中 **严格禁止使用** `CORS_ALLOW_ALL_ORIGINS = True`，必须在 `settings.py` 中明确指定允许的源：

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite默认端口
    "http://127.0.0.1:5173",  # Vite备用地址
]
CORS_ALLOW_CREDENTIALS = True
```

### Celery 配置

项目使用 **Redis** 作为 Celery 的结果后端（不使用数据库）：

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

### 数据库配置

开发环境默认使用 SQLite，生产环境可切换到 MySQL：

```python
# SQLite配置
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
    }
}

# MySQL配置（生产环境）
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', '3306'),
#     }
# }
```

---

## 📁 项目目录结构

### 后端目录结构

```
skillSpace/
├── backend/                     # 后端项目
│   ├── SkillSpace/              # Django主配置
│   │   ├── myapps/              # 应用集合
│   │   │   ├── auth_system/     # 用户认证系统
│   │   │   │   ├── migrations/  # 数据库迁移文件
│   │   │   │   ├── models.py    # 数据模型
│   │   │   │   ├── views.py     # 视图逻辑
│   │   │   │   ├── serializers.py # 序列化器
│   │   │   │   ├── urls.py      # 路由配置
│   │   │   │   ├── admin.py     # 后台管理
│   │   │   │   ├── permissions.py # 权限控制
│   │   │   │   ├── apps.py      # 应用配置
│   │   │   │   └── management/  # 管理命令
│   │   │   ├── resume/          # 简历管理模块
│   │   │   │   ├── migrations/  # 数据库迁移文件
│   │   │   │   ├── models.py    # 数据模型
│   │   │   │   ├── views.py     # 视图逻辑
│   │   │   │   ├── serializers.py # 序列化器
│   │   │   │   ├── urls.py      # 路由配置
│   │   │   │   ├── apps.py      # 应用配置
│   │   │   │   ├── services.py  # 业务逻辑
│   │   │   │   └── utils.py     # 工具函数
│   │   │   ├── tasks_hub/       # 异步任务中心
│   │   │   │   ├── migrations/  # 数据库迁移文件
│   │   │   │   ├── models.py    # 任务模型
│   │   │   │   ├── tasks.py     # Celery任务定义
│   │   │   │   ├── views.py     # API视图
│   │   │   │   ├── urls.py      # 路由配置
│   │   │   │   ├── admin.py     # 后台管理
│   │   │   │   └── apps.py      # 应用配置
│   │   │   ├── ai_demo/         # AI演示模块
│   │   │   │   ├── migrations/  # 数据库迁移文件
│   │   │   │   ├── models.py    # 数据模型
│   │   │   │   ├── views.py     # 视图逻辑
│   │   │   │   ├── serializers.py # 序列化器
│   │   │   │   ├── urls.py      # 路由配置
│   │   │   │   ├── apps.py      # 应用配置
│   │   │   │   ├── model_loader.py # 模型加载器
│   │   │   │   └── admin.py     # 后台管理
│   │   │   ├── __init__.py      # 包初始化文件
│   │   │   ├── models.py        # 共享模型
│   │   │   ├── views.py         # 共享视图
│   │   │   ├── apps.py          # 应用配置
│   │   │   ├── admin.py         # 后台管理
│   │   │   ├── tests.py         # 测试文件
│   │   ├── settings.py          # Django配置
│   │   ├── urls.py              # 主路由配置
│   │   ├── celery.py            # Celery配置
│   │   ├── asgi.py              # ASGI入口
│   │   ├── wsgi.py              # WSGI入口
│   │   └── __init__.py          # 包初始化文件
│   ├── manage.py                # Django管理命令
│   ├── requirements.txt         # Python依赖列表
│   ├── Dockerfile               # Docker构建文件
│   ├── docker-compose.yml       # Docker编排配置
│   ├── .gitignore               # Git忽略配置
│   └── static/                  # 静态文件目录
│       └── avatars/             # 用户头像目录
│
├── frontend/                    # 前端项目
│   └── skillspace/              # Vue3应用
│       ├── src/                 # 源代码目录
│       │   ├── api/             # API接口封装
│       │   │   ├── ai.js        # AI相关API
│       │   │   ├── auth.js      # 认证API
│       │   │   ├── config.js    # API配置
│       │   │   ├── http.js      # HTTP客户端封装
│       │   │   ├── index.js     # API导出
│       │   │   └── resume.js    # 简历相关API
│       │   ├── assets/          # 静态资源
│       │   │   ├── images/      # 图片资源
│       │   │   ├── icons/       # 图标资源
│       │   │   └── fonts/       # 字体资源
│       │   ├── components/      # 公共组件
│       │   │   └── SvgIcon.vue  # SVG图标组件
│       │   ├── composables/     # 组合式函数
│       │   │   └── useAuth.js   # 认证相关逻辑
│       │   ├── styles/          # 样式文件
│       │   │   ├── components.css # 组件样式
│       │   │   ├── global.css   # 全局样式
│       │   │   └── variables.css # CSS变量
│       │   ├── utils/           # 工具函数
│       │   │   └── httpRequest.js # HTTP请求工具
│       │   ├── views/           # 页面组件
│       │   │   ├── dashboard/   # 仪表盘页面
│       │   │   │   ├── modules/     # 子模块
│       │   │   │   │   ├── AiModule.vue      # AI助手模块
│       │   │   │   │   ├── AnalyticsModule.vue  # 数据分析模块
│       │   │   │   │   ├── ProfileModule.vue    # 个人信息模块
│       │   │   │   │   ├── ResumeModule.vue     # 简历管理模块
│       │   │   │   │   └── TasksModule.vue      # 任务中心模块
│       │   │   │   └── DashboardPage.vue    # 仪表盘主页面
│       │   │   ├── login/       # 登录页面
│       │   │   │   └── LoginPage.vue
│       │   │   └── sys/         # 权限管理系统
│       │   │       ├── menu/    # 菜单管理
│       │   │       │   └── index.vue
│       │   │       ├── role/    # 角色管理
│       │   │       │   └── index.vue
│       │   │       └── user/    # 用户管理
│       │   │           └── index.vue
│       │   ├── App.vue          # 根组件
│       │   ├── main.js          # 入口文件
│       │   └── router/          # 路由配置
│       │       └── index.js
│       ├── package.json         # 依赖配置
│       ├── vite.config.js       # Vite配置
│       ├── .gitignore           # Git忽略配置
│       └── index.html           # HTML模板
│
├── .gitignore                   # Git忽略配置
└── README.MD                    # 项目说明文档