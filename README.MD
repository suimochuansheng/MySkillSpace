# SkillSpace - 企业级技能管理与AI助手平台

<div align="center">
  <h3>🎯 一个功能完善的企业级全栈项目</h3>
  <p>基于 Django + Vue3 的前后端分离架构 | RBAC权限管理 | WebSocket实时通信 | AI集成</p>

  ![Django](https://img.shields.io/badge/Django-4.2.27-green.svg)
  ![Vue3](https://img.shields.io/badge/Vue-3.5.24-brightgreen.svg)
  ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
  ![License](https://img.shields.io/badge/License-MIT-yellow.svg)
</div>

---

## 📌 项目概述

**SkillSpace** 是一个面向企业的技能管理与智能助手平台，采用现代化的前后端分离架构。项目展示了从需求分析、系统设计到部署上线的完整开发流程，涵盖了企业级应用所需的核心技术栈和最佳实践。

### 💡 为什么选择这个项目？

- **真实的企业级架构**：完整的RBAC权限体系、操作日志审计、异步任务处理
- **技术栈现代化**：Django 4.2 + Vue3 + WebSocket + AI大模型集成
- **可扩展性强**：模块化设计，支持Docker容器化部署
- **代码质量高**：规范的代码注释、完善的错误处理、安全的权限控制

---

## 🎯 核心技术亮点

### 1️⃣ RBAC权限管理系统
- **三层权限模型**：用户 → 角色 → 菜单/按钮权限
- **细粒度控制**：支持目录、菜单、按钮级别的权限控制
- **动态权限加载**：前端根据用户权限动态渲染菜单和按钮
- **操作日志审计**：记录所有API操作，包含用户、IP、操作内容

**技术实现**：
```python
# 自定义权限装饰器
@permission_required('system:user:edit')
def update_user(request, user_id):
    # 只有拥有 system:user:edit 权限的用户才能访问
    pass
```

### 2️⃣ WebSocket实时通信
- **Django Channels**：基于ASGI的WebSocket支持
- **Redis Channel Layer**：消息队列和分发
- **实时AI对话**：流式输出AI回复内容
- **心跳机制**：自动断线重连

**应用场景**：AI助手实时对话、系统通知推送

### 3️⃣ 分布式异步任务系统
- **Celery + RabbitMQ + Redis**：完整的异步任务架构
- **任务状态追踪**：支持任务进度实时查询
- **定时任务**：支持Cron表达式定时执行
- **任务优先级**：支持高中低优先级队列

**典型任务**：
- 邮件批量发送
- 报告生成（PDF/Excel）
- 数据导入导出
- AI模型推理任务

### 4️⃣ AI大模型集成
- **Transformers库**：支持Hugging Face模型生态
- **流式生成**：支持流式输出，提升用户体验
- **模型热加载**：开发环境支持禁用AI加快启动
- **多模型支持**：兼容阿里云百炼、OpenAI等API

**技术方案**：
```python
# 异步加载AI模型，支持流式输出
async def stream_chat(message):
    for chunk in model.generate_stream(message):
        yield chunk
```

### 5️⃣ 安全性设计
- ✅ **CSRF防护**：Django内置CSRF中间件
- ✅ **CORS严格控制**：禁止 `CORS_ALLOW_ALL_ORIGINS`，白名单管理
- ✅ **密码加密**：Django PBKDF2 算法
- ✅ **会话管理**：HttpOnly Cookie + SameSite
- ✅ **SQL注入防护**：Django ORM参数化查询
- ✅ **XSS防护**：前端自动转义

---

## 🏗️ 系统架构

![image-20251216194129101](D:\softwarefile\typoraFile\typora_image\image-20251216194129101.png)

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层 (Vue3)                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ 用户管理 │  │ 角色管理 │  │ 菜单管理 │  │ AI助手  │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API / WebSocket
┌────────────────────────┼────────────────────────────────────┐
│                      中间层 (Nginx)                          │
│                  反向代理 + 负载均衡                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│                    后端层 (Django)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 认证授权模块  │  │ 权限管理模块  │  │ 业务逻辑模块  │      │
│  │ - JWT/Session│  │ - RBAC       │  │ - 简历管理    │      │
│  │ - 用户管理   │  │ - 操作日志    │  │ - AI对话      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│                   异步任务层 (Celery)                        │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│  │ 邮件发送 │    │ 报告生成 │    │ AI推理  │                 │
│  └─────────┘    └─────────┘    └─────────┘                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│                    数据层                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  MySQL   │  │  Redis   │  │ RabbitMQ │  │  OSS     │    │
│  │ 业务数据  │  │ 缓存/会话 │  │ 消息队列  │  │ 文件存储  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 功能模块详解

### 🔐 用户认证系统 (auth_system)
基于Django自定义用户模型的完整认证体系

**核心功能**：
- ✅ 邮箱登录/注册
- ✅ 会话管理（Session/JWT可选）
- ✅ 用户CRUD操作
- ✅ 角色分配与权限控制
- ✅ 操作日志审计中间件

**技术亮点**：
- 自定义 `AbstractBaseUser` 和 `UserManager`
- 中间件记录所有API操作日志
- 前端权限指令 `v-permission`

**数据模型**：
```python
User (用户)
  ├── roles (多对多) → Role (角色)
  │                      └── menus (多对多) → Menu (菜单)
  └── logs (一对多) → OperationLog (操作日志)
```

### 📝 简历管理模块 (resume)
在线简历编辑与管理系统

**核心功能**：
- ✅ 多维度简历管理（基本信息、教育经历、项目经验、技能特长）
- ✅ AI简历诊断与优化建议
- ✅ 简历导出（PDF/Word）
- ✅ 简历模板系统

**技术实现**：
- Service层分离业务逻辑
- PDF生成（pdfplumber + reportlab）
- AI简历分析（大模型集成）

### 🤖 AI助手模块 (ai_demo)
智能对话与内容生成

**核心功能**：
- ✅ 实时AI对话（WebSocket流式输出）
- ✅ 对话历史管理
- ✅ 多轮上下文对话
- ✅ AI代码生成与解释

**技术架构**：
```python
WebSocket Consumer
  └── ModelLoader (单例模式)
        └── Transformers Pipeline
              ├── 模型热加载
              └── 流式生成器
```

### ⚙️ 任务中心 (tasks_hub)
基于Celery的异步任务系统

**核心功能**：
- ✅ 异步任务提交
- ✅ 任务状态查询
- ✅ 定时任务调度
- ✅ 任务失败重试

**典型任务**：
```python
@shared_task(bind=True, max_retries=3)
def send_bulk_email(self, user_ids, template_id):
    try:
        # 批量发送邮件
        for user_id in user_ids:
            send_email_to_user(user_id, template_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

### 📊 系统监控模块 (monitor)
实时系统状态监控

**核心功能**：
- ✅ 系统资源监控（CPU、内存、磁盘）
- ✅ 数据库连接池状态
- ✅ Redis连接状态
- ✅ Celery Worker状态
- ✅ API请求统计

---

## 🛠️ 技术栈详解

### 后端技术栈

| 技术 | 版本 | 用途 | 核心价值 |
|------|------|------|---------|
| **Django** | 4.2.27 | Web框架 | ORM、中间件、Admin后台 |
| **Django REST Framework** | 3.16.1 | API构建 | 序列化、认证、权限控制 |
| **Django Channels** | 最新 | WebSocket | 实时双向通信 |
| **Celery** | 5.6.0 | 异步任务 | 分布式任务队列 |
| **RabbitMQ** | 最新 | 消息中间件 | Celery Broker |
| **Redis** | 7.1.0 | 缓存/会话 | Celery结果存储 + Channel Layer |
| **MySQL** | 8.0 | 数据库 | 生产环境数据存储 |
| **Transformers** | 4.57.3 | AI模型 | Hugging Face模型库 |
| **PyTorch** | 2.4.1 | 深度学习 | 模型推理框架 |
| **django-cors-headers** | 4.9.0 | CORS | 跨域资源共享 |
| **django-simpleui** | 2025.5.262 | Admin美化 | 后台界面优化 |
| **python-dotenv** | 1.2.1 | 环境变量 | 配置管理 |

### 前端技术栈

| 技术 | 版本 | 用途 | 核心价值 |
|------|------|------|---------|
| **Vue 3** | 3.5.24 | 前端框架 | Composition API、响应式系统 |
| **Vite** | 7.2.4 | 构建工具 | 快速开发、HMR |
| **Element Plus** | 2.11.9 | UI组件库 | 企业级组件 |
| **Vue Router** | 4.6.3 | 路由管理 | 单页应用路由 |
| **Pinia** | 2.1.7 | 状态管理 | 全局状态存储 |
| **ECharts** | 6.0.0 | 数据可视化 | 图表展示 |
| **Axios** | 1.13.2 | HTTP客户端 | API请求封装 |
| **Shiki** | 3.20.0 | 代码高亮 | Markdown代码块渲染 |

### 开发与部署

| 工具 | 用途 |
|------|------|
| **Git** | 版本控制 |
| **Docker** | 容器化部署 |
| **Docker Compose** | 多容器编排 |
| **Nginx** | 反向代理、负载均衡 |
| **VSCode** | 开发工具（完整调试配置） |
| **Flower** | Celery任务监控 |

---

## 🚀 快速开始

### 环境要求

- **Python**: ≥ 3.8（推荐 3.9+）
- **Node.js**: ≥ 16.x（推荐 18.x LTS）
- **MySQL**: ≥ 8.0（生产环境）
- **Redis**: ≥ 6.2
- **RabbitMQ**: ≥ 3.x（可选，使用异步任务时需要）

### 一、后端环境配置

#### 1. 克隆项目并创建虚拟环境

```bash
git clone <repository-url> skillSpace
cd skillSpace/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 如需GPU支持（可选）
pip install torch==2.4.1+cu124 torchvision==0.19.1+cu124 torchaudio==2.4.1+cu124 --index-url https://download.pytorch.org/whl/cu124
```

#### 3. 配置环境变量

在 `backend/` 目录创建 `.env` 文件：

```env
# ========== Django配置 ==========
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True

# ========== 数据库配置 ==========
# 开发环境（SQLite）
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# 生产环境（MySQL）
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=skillspace
# DB_USER=root
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=3306

# ========== Redis配置 ==========
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=123456

# ========== Celery配置 ==========
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://:123456@localhost:6379/0

# ========== AI配置（可选）==========
# OPENAI_API_KEY=sk-...
# ALIBABA_API_KEY=sk-...
```

#### 4. 初始化数据库

```bash
cd backend/SkillSpace

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 初始化菜单数据（可选）
python manage.py init_menus
```

#### 5. 启动后端服务

```bash
# 启动Django开发服务器
python manage.py runserver

# 访问：
# - API: http://127.0.0.1:8000/
# - Admin后台: http://127.0.0.1:8000/admin/
```

#### 6. 启动Celery Worker（可选）

```bash
# 新开终端，激活虚拟环境后执行
cd backend/SkillSpace

# Linux/macOS
celery -A SkillSpace worker --loglevel=info

# Windows
celery -A SkillSpace worker --loglevel=info --pool=solo
```

### 二、前端环境配置

#### 1. 安装依赖

```bash
cd frontend/skillspace
npm install
```

#### 2. 启动开发服务器

```bash
npm run dev

# 访问：http://localhost:5173/
```

#### 3. 构建生产版本

```bash
npm run build

# 预览构建结果
npm run preview
```

### 三、Docker快速部署（推荐）

```bash
# 启动所有服务（MySQL、Redis、RabbitMQ）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止所有服务
docker-compose down
```

---

## 💻 开发环境配置

### VSCode调试环境（一键启动）

项目已配置完整的VSCode调试环境，支持：

- ✅ Django后端断点调试
- ✅ Celery异步任务调试
- ✅ 前后端同时启动（全栈调试）
- ✅ 单个Python文件运行
- ✅ Django管理命令调试

#### 快速开始

```bash
# 1. 打开工作区
code skillspace.code-workspace

# 2. 安装推荐扩展（VSCode会自动提示）

# 3. 选择Python解释器
#    Ctrl+Shift+P → Python: Select Interpreter
#    选择 venv\Scripts\python.exe

# 4. 按F5选择调试配置启动
```

#### 调试配置列表

| 配置名称 | 用途 | 快捷键 |
|---------|------|--------|
| Django: 启动后端服务器 | 完整功能开发 | F5 |
| Django: 启动后端服务器 (禁用AI) | 快速启动 | F5 |
| 全栈调试: Django + 前端 | 同时启动前后端 | F5 |
| Celery: 启动Worker | 异步任务调试 | F5 |
| Python: 当前文件 | 运行单个文件 | F5 |

详细文档：[.vscode/README.md](.vscode/README.md)

---

## 📂 项目目录结构

```
skillSpace/
├── backend/                          # 后端项目
│   ├── SkillSpace/                   # Django主配置
│   │   ├── myapps/                   # 应用集合
│   │   │   ├── auth_system/          # 🔐 用户认证系统
│   │   │   │   ├── models.py         # 用户、角色、菜单模型
│   │   │   │   ├── views.py          # 登录、注册、权限API
│   │   │   │   ├── serializers.py    # 序列化器
│   │   │   │   ├── permissions.py    # 权限控制类
│   │   │   │   ├── middleware.py     # 操作日志中间件
│   │   │   │   └── management/       # 初始化菜单命令
│   │   │   ├── resume/               # 📝 简历管理模块
│   │   │   │   ├── models.py         # 简历数据模型
│   │   │   │   ├── views.py          # 简历CRUD API
│   │   │   │   ├── services.py       # 业务逻辑层
│   │   │   │   └── utils.py          # PDF导出工具
│   │   │   ├── tasks_hub/            # ⚙️ 异步任务中心
│   │   │   │   ├── models.py         # 任务记录模型
│   │   │   │   ├── tasks.py          # Celery任务定义
│   │   │   │   └── views.py          # 任务提交/查询API
│   │   │   ├── ai_demo/              # 🤖 AI助手模块
│   │   │   │   ├── models.py         # 对话历史模型
│   │   │   │   ├── consumers.py      # WebSocket消费者
│   │   │   │   ├── model_loader.py   # AI模型加载器
│   │   │   │   └── ai_engine.py      # AI推理引擎
│   │   │   └── monitor/              # 📊 系统监控模块
│   │   │       ├── views.py          # 监控数据API
│   │   │       └── utils.py          # 系统信息采集
│   │   ├── settings.py               # Django配置
│   │   ├── urls.py                   # 路由配置
│   │   ├── celery.py                 # Celery配置
│   │   ├── asgi.py                   # ASGI入口（WebSocket）
│   │   └── wsgi.py                   # WSGI入口（HTTP）
│   ├── manage.py                     # Django管理命令
│   ├── requirements.txt              # Python依赖
│   ├── Dockerfile                    # Docker镜像
│   └── docker-compose.yml            # 容器编排
│
├── frontend/                         # 前端项目
│   └── skillspace/
│       ├── src/
│       │   ├── api/                  # API接口封装
│       │   │   ├── auth.js           # 认证API
│       │   │   ├── resume.js         # 简历API
│       │   │   ├── ai.js             # AI对话API
│       │   │   └── http.js           # HTTP客户端配置
│       │   ├── components/           # 公共组件
│       │   ├── views/                # 页面组件
│       │   │   ├── login/            # 登录页
│       │   │   ├── dashboard/        # 仪表盘
│       │   │   └── sys/              # 系统管理
│       │   │       ├── user/         # 用户管理
│       │   │       ├── role/         # 角色管理
│       │   │       └── menu/         # 菜单管理
│       │   ├── router/               # 路由配置
│       │   ├── directives/           # 自定义指令
│       │   │   └── permission.js     # 权限指令
│       │   ├── utils/                # 工具函数
│       │   └── main.js               # 入口文件
│       ├── package.json              # 依赖配置
│       └── vite.config.js            # Vite配置
│
├── .vscode/                          # VSCode配置
│   ├── launch.json                   # 调试配置
│   ├── tasks.json                    # 任务配置
│   └── README.md                     # 调试文档
│
├── skillspace.code-workspace         # VSCode工作区
└── README.md                         # 项目文档
```

---

## 🔒 安全性配置

### CORS跨域配置

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite默认端口
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True  # 允许携带Cookie
```

⚠️ **严禁使用** `CORS_ALLOW_ALL_ORIGINS = True`

### CSRF防护

```python
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CSRF_COOKIE_HTTPONLY = False  # 允许JS读取CSRF token
```

### 会话安全

```python
SESSION_COOKIE_HTTPONLY = True  # 防止XSS攻击
SESSION_COOKIE_SAMESITE = 'Lax'  # 防止CSRF攻击
SESSION_COOKIE_AGE = 86400  # 24小时过期
```

---

## 🎓 技术难点与解决方案

### 1. RBAC权限系统设计

**问题**：如何实现灵活的权限控制，支持菜单和按钮级别的权限？

**解决方案**：
- 三层模型：User → Role → Menu
- 菜单支持三种类型：目录(M)、菜单(C)、按钮(F)
- 权限标识字符串：`system:user:edit`
- 前端自定义指令：`v-permission="['system:user:edit']"`

### 2. WebSocket实时通信

**问题**：如何实现AI对话的流式输出？

**解决方案**：
- Django Channels + Redis Channel Layer
- WebSocket Consumer异步处理
- 生成器函数实现流式输出
- 前端EventSource接收SSE流

```python
# consumers.py
async def receive(self, text_data):
    message = json.loads(text_data)

    # 流式生成AI回复
    async for chunk in ai_engine.generate_stream(message['content']):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'content': chunk
        }))
```

### 3. Celery任务状态管理

**问题**：如何追踪异步任务的执行状态和结果？

**解决方案**：
- Redis存储任务结果
- `bind=True` 获取任务实例
- 自定义状态更新
- 前端轮询任务状态API

```python
@shared_task(bind=True)
def long_running_task(self, params):
    # 更新任务进度
    self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100})
    # 执行任务逻辑
    result = do_something(params)
    return {'status': 'success', 'result': result}
```

### 4. AI模型加载优化

**问题**：AI模型加载耗时长，影响开发体验？

**解决方案**：
- 单例模式加载模型
- 开发环境支持禁用AI（环境变量控制）
- 懒加载：首次使用时才加载
- GPU/CPU自动切换

```python
class ModelLoader:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(self):
        if self._model is None:
            self._model = self._load_model()
        return self._model
```

### 5. 操作日志审计

**问题**：如何记录所有API操作，用于安全审计？

**解决方案**：
- 自定义Django中间件
- 记录用户、IP、请求路径、参数、结果
- 异步写入数据库（避免阻塞请求）
- 支持敏感数据脱敏

```python
class OperationLogMiddleware:
    def __call__(self, request):
        response = self.get_response(request)

        # 异步记录日志
        log_operation.delay(
            user=request.user.id,
            ip=get_client_ip(request),
            path=request.path,
            method=request.method,
            status=response.status_code
        )

        return response
```

---

## 📊 项目数据统计

| 指标 | 数据 |
|------|------|
| **代码行数** | ~8000+ 行 |
| **API接口** | 40+ 个 |
| **数据模型** | 15+ 个 |
| **前端页面** | 10+ 个 |
| **第三方依赖** | 100+ 个 |
| **开发周期** | 持续迭代 |

---

## 🚢 部署指南

### Docker部署（推荐）

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 前端静态文件
    location / {
        root /var/www/skillspace/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📈 项目亮点总结

### 技术深度
- ✅ **RBAC权限系统**：三层权限模型，细粒度控制
- ✅ **WebSocket实时通信**：Django Channels + Redis
- ✅ **分布式异步任务**：Celery + RabbitMQ + Redis
- ✅ **AI大模型集成**：Transformers + 流式输出
- ✅ **操作日志审计**：自定义中间件 + 异步记录

### 工程能力
- ✅ **前后端分离**：Django REST Framework + Vue3
- ✅ **代码规范**：详细注释、统一风格
- ✅ **安全性设计**：CSRF、CORS、XSS、SQL注入防护
- ✅ **可扩展性**：模块化设计、Service层分离
- ✅ **容器化部署**：Docker + Docker Compose

### 开发效率
- ✅ **VSCode调试**：完整的调试配置
- ✅ **环境管理**：python-dotenv + .env
- ✅ **Admin后台**：django-simpleui美化
- ✅ **API文档**：REST Framework自动生成

---

## 🎯 适用场景

### 求职简历项目
- 展示全栈开发能力
- 体现系统设计思维
- 证明工程实践经验

### 学习参考项目
- Django高级特性应用
- Vue3 Composition API实践
- 微服务架构思想
- 安全性最佳实践

### 二次开发基础
- 快速搭建企业应用
- 权限系统开箱即用
- AI功能快速集成

---

## 📝 常见问题

### Q: 如何禁用AI功能加快启动速度？
A: 设置环境变量 `DISABLE_AI=True` 或使用VSCode调试配置"Django: 启动后端服务器 (禁用AI)"

### Q: 如何切换到MySQL数据库？
A: 在 `.env` 文件中配置MySQL参数，Django会自动切换

### Q: WebSocket连接失败怎么办？
A: 检查Redis是否启动，Channel Layer配置是否正确

### Q: Celery任务无法执行？
A: 确保RabbitMQ和Celery Worker都已启动

---

## 📄 开源协议

本项目采用 MIT 协议开源，可自由用于学习和商业用途。

---

## 👨‍💻 关于作者

这是我的个人全栈项目，展示了从需求分析、系统设计到编码实现的完整流程。如果你对项目有任何疑问或建议，欢迎交流！

**技能栈**：Python、Django、Vue.js、MySQL、Redis、Docker

**擅长领域**：后端开发、系统架构、权限管理、AI集成

---

<div align="center">
  <p>⭐ 如果这个项目对你有帮助，请给个Star支持一下！</p>
  <p>📧 联系方式：[huazhu7k7k@163.com]</p>
</div>
