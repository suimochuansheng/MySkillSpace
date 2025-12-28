#!/bin/bash
# Docker容器监控快速修复脚本
# 用途：快速部署修复后的代码（使用Docker SDK）

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Docker容器监控快速修复"
echo "=========================================="
echo ""

# 1. 检查当前位置
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ 错误：请在项目根目录执行此脚本"
    exit 1
fi

# 2. 拉取最新代码
echo "📥 [1/5] 拉取最新代码..."
git pull origin feature/RBAC_reconstruction

# 3. 重新构建后端镜像（安装docker==7.1.0）
echo "🔨 [2/5] 重新构建后端镜像（约3-5分钟）..."
cd backend
docker build -t ${ACR_REGISTRY}/${ACR_NAMESPACE}/backend:latest . \
    --build-arg BUILDKIT_INLINE_CACHE=1

cd ..

# 4. 重启后端容器
echo "🔄 [3/5] 重启后端容器..."
docker-compose -f docker-compose.prod.yml up -d backend

# 5. 等待服务启动
echo "⏳ [4/5] 等待后端服务启动（30秒）..."
sleep 30

# 6. 验证修复
echo "✅ [5/5] 验证修复..."
docker logs skillspace_backend --tail 50 | grep -E "Docker容器采集|ERROR.*docker"

echo ""
echo "=========================================="
echo "修复完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 访问系统监控 → 云服务器监控"
echo "2. 查看容器列表是否显示"
echo "3. 使用Dozzle查看实时日志: http://$(curl -s ifconfig.me):9999"
echo ""
