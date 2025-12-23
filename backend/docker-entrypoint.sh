#!/bin/bash
# ==================== Docker容器启动脚本 ====================
# 用途：等待数据库启动、运行迁移、启动服务

set -e  # 遇到错误立即退出

# 颜色输出（方便查看日志）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SkillSpace Backend 启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# ==================== 1. 等待数据库启动 ====================
echo -e "${YELLOW}[1/4] 等待数据库启动...${NC}"

# 从环境变量获取数据库配置
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}

# 等待数据库端口可用（最多等待30秒）
timeout=30
counter=0

while ! nc -z $DB_HOST $DB_PORT; do
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        echo -e "${RED}错误：数据库启动超时！${NC}"
        exit 1
    fi
    echo -e "等待数据库 $DB_HOST:$DB_PORT... ($counter/$timeout)"
    sleep 1
done

echo -e "${GREEN}✓ 数据库已就绪${NC}"
sleep 2  # 额外等待2秒，确保数据库完全启动

# ==================== 2. 运行数据库迁移 ====================
echo -e "${YELLOW}[2/4] 运行数据库迁移...${NC}"

# 注意：manage.py 在 /app 目录下，不是 /app/SkillSpace
cd /app

# 检查是否有新的迁移
if python manage.py showmigrations | grep '\[ \]'; then
    echo "发现未应用的迁移，开始迁移..."
    python manage.py migrate --noinput
    echo -e "${GREEN}✓ 数据库迁移完成${NC}"
else
    echo -e "${GREEN}✓ 数据库已是最新状态${NC}"
fi

# ==================== 3. 收集静态文件 ====================
echo -e "${YELLOW}[3/4] 收集静态文件...${NC}"

# 收集Django和第三方应用的静态文件到STATIC_ROOT
python manage.py collectstatic --noinput --clear

echo -e "${GREEN}✓ 静态文件收集完成${NC}"

# ==================== 4. 启动服务 ====================
echo -e "${YELLOW}[4/4] 启动服务...${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SkillSpace Backend 启动成功！${NC}"
echo -e "${GREEN}  监听端口: 8000${NC}"
echo -e "${GREEN}  ASGI服务器: Daphne${NC}"
echo -e "${GREEN}========================================${NC}"

# 执行传入的命令（默认是 daphne ...）
exec "$@"
