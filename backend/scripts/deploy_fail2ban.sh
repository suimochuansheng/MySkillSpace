#!/bin/bash
# fail2ban快速部署脚本
# 用途：在阿里云服务器上快速配置fail2ban防暴力破解
# 执行：sudo bash deploy_fail2ban.sh
# 注意：必须在项目根目录执行（/root/skillspace）

set -e  # 遇到错误立即退出

echo "=========================================="
echo "fail2ban防暴力破解 - 快速部署"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户执行此脚本"
    echo "   运行：sudo bash backend/scripts/deploy_fail2ban.sh"
    exit 1
fi

# 检查是否在项目根目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ 请在项目根目录执行此脚本"
    echo "   示例：cd /root/skillspace && sudo bash backend/scripts/deploy_fail2ban.sh"
    exit 1
fi

# 获取当前目录（项目根目录）
PROJECT_ROOT=$(pwd)
LOG_DIR="${PROJECT_ROOT}/logs/backend"
LOG_FILE="${LOG_DIR}/login_fail.log"

echo "📍 项目根目录: ${PROJECT_ROOT}"
echo "📍 日志目录: ${LOG_DIR}"
echo "📍 日志文件: ${LOG_FILE}"
echo ""

# 1. 安装fail2ban
echo "📦 [1/6] 安装fail2ban..."
apt-get update -qq
apt-get install -y fail2ban iptables-persistent

# 检查安装
if ! command -v fail2ban-client &> /dev/null; then
    echo "❌ fail2ban安装失败"
    exit 1
fi

echo "✅ fail2ban已安装：$(fail2ban-client --version)"

# 2. 创建日志目录和文件
echo "📁 [2/6] 创建日志目录和文件..."
mkdir -p "${LOG_DIR}"
touch "${LOG_FILE}"
chmod 666 "${LOG_FILE}"

echo "✅ 日志文件已创建：${LOG_FILE}"

# 3. 创建fail2ban过滤规则
echo "📝 [3/6] 创建fail2ban过滤规则..."
cat > /etc/fail2ban/filter.d/django-login.conf << 'EOF'
# fail2ban过滤规则：Django登录失败
# 文件路径：/etc/fail2ban/filter.d/django-login.conf

[Definition]

# 失败模式匹配（匹配日志中的IP地址）
failregex = ^.*登录失败.*IP: <HOST>$

# 忽略模式
ignoreregex =
EOF

echo "✅ 过滤规则已创建：/etc/fail2ban/filter.d/django-login.conf"

# 4. 创建fail2ban监狱配置
echo "📝 [4/6] 创建fail2ban监狱配置..."
cat > /etc/fail2ban/jail.d/django-login.conf << EOF
# fail2ban监狱配置：Django登录保护
# 文件路径：/etc/fail2ban/jail.d/django-login.conf

[django-login]
enabled = true
filter = django-login
logpath = ${LOG_FILE}
maxretry = 5
findtime = 600
bantime = 3600
port = 80,443
action = iptables-multiport[name=django-login, port="80,443", protocol=tcp]
EOF

echo "✅ 监狱配置已创建：/etc/fail2ban/jail.d/django-login.conf"

# 5. 重启fail2ban
echo "🔄 [5/6] 重启fail2ban服务..."
systemctl restart fail2ban
systemctl enable fail2ban

sleep 2

# 6. 验证配置
echo "✅ [6/6] 验证配置..."
echo ""
echo "fail2ban服务状态："
systemctl status fail2ban --no-pager | head -5

echo ""
echo "已启用的监狱："
fail2ban-client status

echo ""
echo "django-login监狱详情："
fail2ban-client status django-login 2>/dev/null || echo "  (监狱正在初始化...)"

echo ""
echo "=========================================="
echo "✅ fail2ban部署完成！"
echo "=========================================="
echo ""
echo "配置信息："
echo "  - 最大重试次数：5次"
echo "  - 时间窗口：10分钟"
echo "  - 封禁时长：1小时"
echo "  - 监控日志：${LOG_FILE}"
echo ""
echo "下一步："
echo "  1. 重启Docker容器（日志已自动挂载）："
echo "     docker compose -f docker-compose.prod.yml restart backend"
echo "  2. 测试fail2ban封禁效果（连续5次登录失败）"
echo "  3. 在前端访问 系统管理 → 封禁IP管理 查看封禁列表"
echo ""
echo "常用命令："
echo "  - 查看封禁列表：fail2ban-client status django-login"
echo "  - 解封IP：fail2ban-client set django-login unbanip <IP>"
echo "  - 查看fail2ban日志：tail -f /var/log/fail2ban.log"
echo "  - 查看登录失败日志：tail -f ${LOG_FILE}"
echo ""
