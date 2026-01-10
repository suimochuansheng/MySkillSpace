# SkillSpace 脚本与工具集

> 本目录包含项目的初始化脚本、部署工具、开发辅助脚本和相关文档

## 📂 目录结构

```
scripts/
├── deployment/          # 部署相关脚本
├── database/           # 数据库初始化和迁移脚本
├── dev-tools/          # 开发工具和辅助脚本
├── env-config/         # 环境配置脚本
└── docs/               # 项目文档和指南
```

---

## 🚀 部署脚本 (deployment/)

### deploy-to-debian.sh
**功能**: 一键部署到 Debian 服务器
**用途**: 自动化部署流程，包括环境检查、依赖安装、服务启动
**使用场景**: 生产环境首次部署或更新
**执行方式**:
```bash
cd /home/huazhu/MySkillSpace/scripts/deployment
chmod +x deploy-to-debian.sh
./deploy-to-debian.sh
```

### docker-entrypoint.sh
**功能**: Docker 容器启动入口脚本
**用途**: 容器启动时自动执行初始化任务（数据库迁移、静态文件收集等）
**使用场景**: Docker 容器化部署
**说明**: 由 Dockerfile 自动调用，无需手动执行

---

## 💾 数据库脚本 (database/)

### init_db.sql
**功能**: PostgreSQL 数据库初始化脚本
**用途**: 启用必要的 PostgreSQL 扩展（pgvector、pg_trgm、uuid-ossp）
**使用场景**: 首次启动 PostgreSQL 容器时自动执行
**说明**:
- 启用 pgvector 扩展（向量存储，为 RAG 未来功能预留）
- 启用 pg_trgm 扩展（全文搜索和模糊匹配）
- 启用 uuid-ossp 扩展（生成 UUID）

### switch_to_pg.sh
**功能**: 从 SQLite 切换到 PostgreSQL（原始版本）
**用途**: 迁移开发环境数据库到 PostgreSQL
**使用场景**: 开发环境数据库迁移
**说明**: 已被 switch_to_pg_fixed.sh 替代

### switch_to_pg_fixed.sh
**功能**: 从 SQLite 切换到 PostgreSQL（修复版）
**用途**: 完整的数据库迁移流程，包含错误处理和数据备份
**使用场景**: 推荐使用此版本进行数据库迁移
**执行方式**:
```bash
cd /home/huazhu/MySkillSpace/scripts/database
chmod +x switch_to_pg_fixed.sh
./switch_to_pg_fixed.sh
```

### clear_migrations.py
**功能**: 清理 Django 迁移文件
**用途**: 删除所有应用的迁移文件，用于重置数据库迁移历史
**使用场景**: 开发环境重置数据库结构
**警告**: ⚠️ 危险操作！仅在开发环境使用，生产环境禁用
**执行方式**:
```bash
cd /home/huazhu/MySkillSpace/backend
python ../scripts/database/clear_migrations.py
```

---

## 🛠️ 开发工具 (dev-tools/)

### format-code.sh
**功能**: 代码格式化工具
**用途**: 使用 Black、isort、Prettier 等工具自动格式化代码
**使用场景**: 提交代码前格式化
**执行方式**:
```bash
cd /home/huazhu/MySkillSpace/scripts/dev-tools
chmod +x format-code.sh
./format-code.sh
```

### fix_line_endings.sh
**功能**: 修复 Windows 换行符问题
**用途**: 将所有 .sh 脚本的 CRLF 换行符转换为 LF
**使用场景**: 在 Windows 环境下创建脚本后，在 Linux 环境执行前使用
**执行方式**:
```bash
cd /home/huazhu/MySkillSpace/scripts/dev-tools
chmod +x fix_line_endings.sh
./fix_line_endings.sh
```

### monitor_celery.py
**功能**: Celery 任务队列监控脚本
**用途**: 实时监控 Celery Worker 状态和任务执行情况
**使用场景**: 调试异步任务问题
**执行方式**:
```bash
cd /home/huazhu/MySkillSpace/backend
python ../scripts/dev-tools/monitor_celery.py
```

---

## ⚙️ 环境配置 (env-config/)

### update_wsl_ip.sh
**功能**: 自动更新 WSL2 IP 地址
**用途**: 自动更新 Django settings.py 中的 CORS 允许地址
**使用场景**: WSL2 环境开发，每次重启后 IP 变化时使用
**执行方式**:
```bash
cd /home/huazhu/MySkillSpace/scripts/env-config
chmod +x update_wsl_ip.sh
./update_wsl_ip.sh
```
**说明**: 会自动检测当前 WSL2 IP 并更新 `CORS_ALLOWED_ORIGINS` 配置

### fix_docker_monitor.sh
**功能**: 修复 Docker 容器监控问题
**用途**: 解决 Docker SDK 权限问题和配置错误
**使用场景**: Docker 监控功能异常时使用
**执行方式**:
```bash
cd /home/huazhu/MySkillSpace/scripts/env-config
chmod +x fix_docker_monitor.sh
./fix_docker_monitor.sh
```

---

## 📚 项目文档 (docs/)

### MIGRATION_GUIDE.md
**内容**: 数据库迁移指南
**说明**: 详细的 SQLite 到 PostgreSQL 迁移步骤和注意事项

### POSTGRES_SETUP_GUIDE.md
**内容**: PostgreSQL 配置指南
**说明**: PostgreSQL 安装、配置、pgvector 扩展启用等

### project_tree.txt
**内容**: 项目完整目录结构
**说明**: 自动生成的项目文件树，用于快速了解项目结构

### 图组.md
**内容**: 项目架构图和流程图
**说明**: 使用 Mermaid 或其他工具绘制的项目架构图

---

## 📌 使用建议

### 首次部署流程
1. **环境配置**: 运行 `env-config/update_wsl_ip.sh`（WSL2 环境）
2. **数据库初始化**: 启动 PostgreSQL 容器（自动执行 `database/init_db.sql`）
3. **数据库迁移**: 运行 `database/switch_to_pg_fixed.sh`
4. **部署应用**: 运行 `deployment/deploy-to-debian.sh`

### 开发环境维护
- **格式化代码**: 提交前运行 `dev-tools/format-code.sh`
- **修复换行符**: Windows 环境创建脚本后运行 `dev-tools/fix_line_endings.sh`
- **监控任务**: 调试异步任务时运行 `dev-tools/monitor_celery.py`

### Docker 部署
- 容器启动时会自动执行 `deployment/docker-entrypoint.sh`
- 数据库扩展由 `database/init_db.sql` 自动启用

---

## ⚠️ 注意事项

1. **权限设置**: 所有 `.sh` 脚本需要添加执行权限 (`chmod +x <script>.sh`)
2. **路径问题**: 部分脚本使用绝对路径，执行前请确认路径正确
3. **环境变量**: 确保已配置 `.env` 文件中的必要环境变量
4. **备份数据**: 执行数据库相关脚本前，务必备份数据
5. **生产环境**: `clear_migrations.py` 等危险脚本仅限开发环境使用

---

## 🔧 故障排查

### 脚本执行权限错误
```bash
# 批量添加执行权限
find scripts/ -name "*.sh" -exec chmod +x {} \;
```

### Windows 换行符问题
```bash
# 批量修复换行符
./scripts/dev-tools/fix_line_endings.sh
```

### PostgreSQL 扩展未启用
```bash
# 手动执行 SQL 脚本
psql -U postgres -d skillspace -f scripts/database/init_db.sql
```

---

**最后更新**: 2026-01-10
**维护者**: SkillSpace Team
