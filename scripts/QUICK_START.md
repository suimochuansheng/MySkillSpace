# 脚本快速使用指南

> 快速索引：如何使用 scripts/ 目录下的各类脚本

## 🚀 快速导航

### 我想...

#### 部署项目到服务器
```bash
cd scripts/deployment
chmod +x deploy-to-debian.sh
./deploy-to-debian.sh
```

#### 初始化 PostgreSQL 数据库
```bash
# 方式1: Docker 自动执行（推荐）
docker-compose up -d postgres
# init_db.sql 会自动执行

# 方式2: 手动执行
psql -U postgres -d skillspace -f scripts/database/init_db.sql
```

#### 从 SQLite 迁移到 PostgreSQL
```bash
cd scripts/database
chmod +x switch_to_pg_fixed.sh
./switch_to_pg_fixed.sh
```

#### 修复 WSL2 IP 地址问题
```bash
cd scripts/env-config
chmod +x update_wsl_ip.sh
./update_wsl_ip.sh
# 然后重启 Django 服务
```

#### 格式化代码
```bash
cd scripts/dev-tools
chmod +x format-code.sh
./format-code.sh
```

#### 修复 Windows 换行符问题
```bash
cd scripts/dev-tools
chmod +x fix_line_endings.sh
./fix_line_endings.sh
```

#### 监控 Celery 任务
```bash
cd backend
python ../scripts/dev-tools/monitor_celery.py
```

#### 清理迁移文件（开发环境）
```bash
cd backend
python ../scripts/database/clear_migrations.py
# ⚠️ 仅用于开发环境！
```

---

## 📂 目录说明

```
scripts/
├── deployment/      → 部署相关脚本
├── database/        → 数据库初始化和迁移
├── dev-tools/       → 开发工具
├── env-config/      → 环境配置
└── docs/            → 项目文档
```

---

## ⚡ 常见场景

### 场景1: 首次在新服务器部署
```bash
# 1. 配置环境（WSL2）
./scripts/env-config/update_wsl_ip.sh

# 2. 启动数据库
docker-compose up -d postgres

# 3. 运行迁移
cd backend
python manage.py migrate

# 4. 部署项目
./scripts/deployment/deploy-to-debian.sh
```

### 场景2: 开发环境数据库重置
```bash
# 1. 清理迁移文件
cd backend
python ../scripts/database/clear_migrations.py

# 2. 删除数据库
docker-compose down -v

# 3. 重新启动数据库
docker-compose up -d postgres

# 4. 重新生成迁移
python manage.py makemigrations
python manage.py migrate
```

### 场景3: 代码提交前准备
```bash
# 1. 格式化代码
./scripts/dev-tools/format-code.sh

# 2. 修复换行符（如果在 Windows 环境创建了脚本）
./scripts/dev-tools/fix_line_endings.sh

# 3. 提交代码
git add .
git commit -m "your commit message"
```

---

## 🔧 故障排查

### 脚本没有执行权限
```bash
# 单个脚本
chmod +x scripts/xxx/xxx.sh

# 批量添加
find scripts/ -name "*.sh" -exec chmod +x {} \;
```

### WSL2 每次重启 IP 都变化
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias fix-ip='cd /home/huazhu/MySkillSpace && ./scripts/env-config/update_wsl_ip.sh'

# 然后每次重启后执行
fix-ip
```

### PostgreSQL 扩展未启用
```bash
# 进入容器
docker exec -it skillspace-postgres-1 psql -U postgres -d skillspace

# 手动启用
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 📚 更多信息

- 完整文档请查看: [scripts/README.md](./README.md)
- 数据库迁移指南: [scripts/docs/MIGRATION_GUIDE.md](./docs/MIGRATION_GUIDE.md)
- PostgreSQL 配置: [scripts/docs/POSTGRES_SETUP_GUIDE.md](./docs/POSTGRES_SETUP_GUIDE.md)

---

**提示**: 执行脚本前，请确保已配置 `.env` 文件！
