# Scripts Directory

这个目录包含了SkillSpace项目的各种工具脚本。

## 📋 脚本列表

### 1. init_system.py - 系统初始化脚本
**用途**: 首次部署时初始化整个系统

**功能**:
- 运行数据库迁移
- 初始化32个菜单
- 创建默认角色（系统管理员、普通用户）
- 创建超级管理员账号
- 为角色分配菜单权限

**使用方法**:
```bash
cd /path/to/skillspace/backend/scripts
python init_system.py
```

**适用场景**:
- 首次部署到服务器
- 重置测试环境
- 数据库迁移后重新初始化

---

### 2. fix_passwords.py - 密码修复工具
**用途**: 检查并修复用户密码问题

**功能**:
- 检查所有用户的密码格式
- 修复明文密码（重新加密）
- 创建测试用户

**使用方法**:
```bash
cd /path/to/skillspace/backend/scripts
python fix_passwords.py
```

**适用场景**:
- 通过Django Admin直接设置密码后无法登录
- 用户密码损坏
- 批量重置密码

---

### 3. test_cloud_monitor.py - 云监控测试脚本
**用途**: 测试云服务器监控配置

**功能**:
- 测试配置文件加载
- 测试SSH连接
- 测试数据采集功能

**使用方法**:
```bash
cd /path/to/skillspace/backend/scripts
python test_cloud_monitor.py
```

**适用场景**:
- 配置云监控后验证
- SSH连接问题排查
- 部署前测试

---

## 🔧 通用使用说明

### 运行脚本的前置要求

1. **激活虚拟环境**:
```bash
# Linux/Mac
source /path/to/venv/bin/activate

# Windows
E:\skillSpace\backend\sk_venv\Scripts\activate
```

2. **确保Django环境正确**:
所有脚本都会自动设置Django环境，但需要确保：
- `DJANGO_SETTINGS_MODULE` 指向正确
- 数据库连接配置正确

### 在Docker环境中运行

```bash
# 进入容器
docker-compose exec web bash

# 运行脚本
cd /app/scripts
python init_system.py
```

---

## 📝 脚本开发规范

### 命名规范
- 使用小写字母
- 单词之间用下划线分隔
- 功能明确的动词开头（如 init_, fix_, test_）

### 代码规范
1. 包含docstring说明用途
2. Django环境设置：
```python
import os
import sys
import django

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkillSpace.settings')
django.setup()
```

3. 错误处理和用户提示
4. 操作确认（对于危险操作）

---

## ⚠️ 注意事项

1. **生产环境谨慎使用**: 某些脚本会修改数据库，使用前请备份
2. **权限检查**: 确保有足够的文件和数据库权限
3. **日志记录**: 重要操作会输出到控制台，建议重定向保存
4. **定期更新**: 系统升级后检查脚本是否需要更新

---

## 🆘 常见问题

### Q: 脚本报错 "No module named 'xxx'"
**A**: 确认虚拟环境已激活，并安装了所有依赖：
```bash
pip install -r ../requirements.txt
```

### Q: 数据库连接失败
**A**: 检查环境变量和数据库配置：
```bash
# 检查环境变量
echo $DATABASE_URL  # Linux/Mac
echo %DATABASE_URL% # Windows

# 或检查 settings.py 中的 DATABASES 配置
```

### Q: 权限不足
**A**: 确保当前用户有数据库和文件的读写权限

---

**最后更新**: 2025-12-25
