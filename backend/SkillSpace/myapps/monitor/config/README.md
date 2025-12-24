# 云服务器监控配置文件使用说明

## 快速开始

### 1. 复制配置模板

```bash
cd E:\skillSpace\backend\SkillSpace\myapps\monitor\config\
copy cloud_servers.example.yaml cloud_servers.yaml
```

### 2. 编辑配置文件

使用文本编辑器打开 `cloud_servers.yaml`，填写你的服务器信息：

```yaml
servers:
  - name: "我的云服务器"
    enabled: true
    tags:
      - production

    connection:
      host: "your-server-ip"      # 填写你的服务器IP
      port: 22
      username: "root"             # 填写SSH用户名
      auth_type: "password"
      password: "your-password"    # 填写密码

    monitoring:
      services:
        - name: "django"
          type: "web"
          process_pattern: "python.*manage.py"
          port: 8000

      enable_docker: true
```

### 3. 启动服务

```bash
cd E:\skillSpace\backend\
python manage.py runserver
```

配置文件会自动加载，云监控自动开始工作。

## 配置文件说明

### 认证方式

#### 密码认证
```yaml
connection:
  auth_type: "password"
  password: "your-password"
```

#### SSH密钥认证
```yaml
connection:
  auth_type: "key"
  private_key_path: "/path/to/private/key.pem"
  # passphrase: "key-password"  # 如果密钥有密码
```

### 服务监控配置

每个服务需要配置以下字段：

- `name`: 服务名称
- `type`: 服务类型（web/database/cache/other）
- `process_pattern`: 进程匹配模式（正则表达式）
- `port`: 服务端口

### 示例：监控多个服务

```yaml
monitoring:
  services:
    - name: "nginx"
      type: "web"
      process_pattern: "nginx"
      port: 80

    - name: "mysql"
      type: "database"
      process_pattern: "mysqld"
      port: 3306

    - name: "redis"
      type: "cache"
      process_pattern: "redis-server"
      port: 6379
```

## 安全建议

1. **文件权限**：设置配置文件权限为仅所有者可读写
   ```bash
   chmod 600 cloud_servers.yaml
   ```

2. **版本控制**：不要将 `cloud_servers.yaml` 提交到Git
   - 已经在 `.gitignore` 中配置排除

3. **密码管理**：
   - 生产环境建议使用SSH密钥认证
   - 如果使用密码，请确保密码强度足够

4. **最小权限**：
   - SSH用户建议使用非root用户
   - 赋予最小必要权限

## 常见问题

### Q: 配置文件在哪里？
A: `E:\skillSpace\backend\SkillSpace\myapps\monitor\config\cloud_servers.yaml`

### Q: 如何添加多台服务器？
A: 在 `servers` 列表中添加多个服务器配置：

```yaml
servers:
  - name: "服务器1"
    enabled: true
    connection:
      host: "ip1"
      # ...

  - name: "服务器2"
    enabled: true
    connection:
      host: "ip2"
      # ...
```

### Q: 如何暂时禁用某台服务器的监控？
A: 将该服务器的 `enabled` 设置为 `false`：

```yaml
- name: "测试服务器"
  enabled: false  # 禁用
```

### Q: 配置修改后需要重启服务吗？
A: 当前版本需要重启Django服务。未来版本会支持热重载。

## 配置验证

启动服务后，检查日志输出：

```
成功加载配置文件: .../cloud_servers.yaml
云服务器监控后台任务已启动
```

如果配置有误，会看到错误提示。

## 下一步

配置完成后：
1. 访问前端监控页面
2. 选择"云服务器监控"标签页
3. 查看实时监控数据

---

**文档版本**: v1.0
**最后更新**: 2025-12-24
