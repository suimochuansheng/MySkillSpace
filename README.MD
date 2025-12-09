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
  基于自定义用户模型的完整认证体系，支持邮箱登录、用户注册、权限管理等功能

- **📝 简历管理（resume）**  
  个人简历在线编辑与管理，支持多维度技能展示、项目经历记录等

- **⚙️ 任务中心（tasks_hub）**  
  基于 Celery 的异步任务处理系统，支持邮件发送、报告生成、数据导出等耗时操作

- **📊 数据看板（Dashboard）**  
  可视化数据分析与展示，包含用户画像、任务统计、数据分析等模块

---

## 🔧 技术栈

### 后端技术

| 类别 | 技术 | 说明 |
|------|------|------|
| **核心框架** | Django 4.2.x | Python Web 框架 |
| **API框架** | Django REST Framework | RESTful API 构建 |
| **数据库** | MySQL 8.0 | 生产环境（支持 SQLite 开发） |
| **异步任务** | Celery 5.5.x | 分布式任务队列 |
| **消息队列** | RabbitMQ / Redis | Celery Broker 与结果后端 |
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
| **HTTP客户端** | Axios | 请求拦截与API调用 |
| **状态管理** | Pinia（可选） | Vue 3 官方状态管理 |
| **开发语言** | JavaScript (ES6+) | 现代化 JavaScript |

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
- **MySQL**: ≥ 8.0（或 SQLite 用于开发）
- **Redis**: ≥ 6.2（可选，用于 Celery）
- **RabbitMQ**: ≥ 3.x（可选，用于 Celery）

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
pip install -r requirements_py39.txt

# 如需GPU支持（CUDA 11.8）
pip install torch==2.1.2+cu118 torchaudio==2.1.2+cu118 torchvision==0.16.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

#### 2.3 配置环境变量

在 `backend/` 目录下创建 `.env` 文件：

```env
# Django配置
SECRET_KEY=your-secret-key-here
DEBUG=True

# 数据库配置（MySQL）
DB_NAME=skillspace
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

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

## 📁 项目目录结构

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
│   │   │   │   └── admin.py     # 后台管理
│   │   │   ├── resume/          # 简历管理模块
│   │   │   └── tasks_hub/       # 异步任务中心
│   │   │       ├── models.py    # 任务模型
│   │   │       ├── tasks.py     # Celery任务定义
│   │   │       └── views.py     # API视图
│   │   ├── settings.py          # Django配置
│   │   ├── urls.py              # 主路由配置
│   │   ├── celery.py            # Celery配置
│   │   └── wsgi.py              # WSGI入口
│   ├── manage.py                # Django管理命令
│   ├── requirements_py39.txt    # Python依赖列表
│   ├── Dockerfile               # Docker构建文件
│   └── docker-compose.yml       # Docker编排配置
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
│       │   ├── styles/          # 样式文件
│       │   │   ├── components.css # 组件样式
│       │   │   ├── global.css   # 全局样式
│       │   │   └── variables.css # CSS变量
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
│       └── index.html           # HTML模板
│
├── .gitignore                   # Git忽略配置
└── README.MD                    # 项目说明文档
```

---

## 🐳 Docker 部署（推荐）

### 使用 Docker Compose 一键启动

```bash
cd backend

# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Docker Compose 包含服务

- **web**: Django 应用服务器（端口 8000）
- **db**: MySQL 数据库（端口 3306）
- **redis**: Redis 缓存服务（端口 6379）
- **rabbitmq**: RabbitMQ 消息队列（端口 5672, 管理界面 15672）
- **celery_worker**: Celery 工作进程
- **celery_beat**: Celery 定时任务

---

## 🛠️ 常用命令

### 后端命令

```bash
# 创建Django应用
python manage.py startapp <app_name>

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic

# 运行测试
python manage.py test

# Django Shell
python manage.py shell
```

### 前端命令

```bash
# 开发环境启动
npm run dev

# 生产构庻
npm run build

# 预览构建结果
npm run preview

# 安装新依赖
npm install <package-name>
```

---

## 📚 API 文档

### 认证相关

- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出
- `GET /api/auth/user/` - 获取当前用户信息

### 简历管理

- `GET /api/resumes/` - 获取简历列表
- `POST /api/resumes/` - 创建简历
- `GET /api/resumes/{id}/` - 获取简历详情
- `PUT /api/resumes/{id}/` - 更新简历
- `DELETE /api/resumes/{id}/` - 删除简历

### 任务中心

- `GET /api/tasks/` - 获取任务列表
- `POST /api/tasks/` - 创建异步任务
- `GET /api/tasks/{id}/` - 查询任务状态

> 📘 **注意**：详细 API 文档请访问：`http://127.0.0.1:8000/api/` （DRF 自带浏览界面）

---

## ⚙️ 配置说明

### CORS 跨域配置

项目中 **严格禁止使用** `CORS_ALLOW_ALL_ORIGINS = True`，必须在 `settings.py` 中明确指定允许的源：

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite默认端口
    "http://127.0.0.1:8080",   # 备用端口
]
CORS_ALLOW_CREDENTIALS = True
```

### Celery 配置

项目使用 **Redis** 作为 Celery 的结果后端（不使用数据库）：

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

---

## 📝 开发规范

### 代码注释

- 所有代码注释**必须使用中文**
- 注释应详细说明模块、函数、类的作用和实现逻辑

### 前端规范

- 使用 Vue3 **Composition API** (`<script setup>`)
- 按需导入 Element Plus 组件
- 界面文本必须使用中文

### 后端规范

- 使用 Django REST Framework 的 ViewSet 和 Serializer
- API 路由使用名词复数形式（如 `/api/users/`）
- 遵循 RESTful 设计原则

---

## 🔒 安全注意事项

1. **不要提交** `.env` 文件到 Git 仓库
2. **生产环境**必须设置 `DEBUG = False`
3. **定期更新** `SECRET_KEY` 并使用强密码
4. **数据库备份**：定期备份 MySQL 数据
5. **CORS 配置**：仅允许可信源访问

---

## 👥 贡献指南



1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交修改 (`git commit -m '添加某个功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

---

## 📝 许可证

此项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件

---

## 📧 联系方式

- **项目主页**: <你的项目主页>
- **问题反馈**: <你的GitHub Issues链接>
- **邮箱**: <你的邮箱>

---

<div align="center">
  <p>⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！</p>
  <p>© 2025 SkillSpace. All rights reserved.</p>
</div>