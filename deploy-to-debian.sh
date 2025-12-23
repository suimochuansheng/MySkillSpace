#!/bin/bash
# ==================== SkillSpace 部署到 Debian13 虚拟机脚本 ====================
# 使用说明：
# 1. 在 Windows 上导出镜像：bash deploy-to-debian.sh export
# 2. 将导出的 tar 文件和此脚本传输到 Debian 虚拟机
# 3. 在 Debian 上导入并运行：sudo bash deploy-to-debian.sh deploy

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置变量
EXPORT_DIR="./docker-images"
IMAGE_PREFIX="skillspace"

# ==================== 函数：导出镜像（在 Windows 上执行）====================
export_images() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  开始导出 Docker 镜像${NC}"
    echo -e "${GREEN}========================================${NC}"

    # 创建导出目录
    mkdir -p "$EXPORT_DIR"

    # 导出前端镜像
    echo -e "${YELLOW}[1/3] 导出前端镜像...${NC}"
    docker save skillspace-frontend:latest -o "$EXPORT_DIR/frontend.tar"
    echo -e "${GREEN}✓ 前端镜像导出完成${NC}"

    # 导出后端镜像
    echo -e "${YELLOW}[2/3] 导出后端镜像...${NC}"
    docker save skillspace-backend:latest -o "$EXPORT_DIR/backend.tar"
    echo -e "${GREEN}✓ 后端镜像导出完成${NC}"

    # 导出 Celery Worker 镜像
    echo -e "${YELLOW}[3/3] 导出 Celery Worker 镜像...${NC}"
    docker save skillspace-celery_worker:latest -o "$EXPORT_DIR/celery_worker.tar"
    echo -e "${GREEN}✓ Celery Worker 镜像导出完成${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  镜像导出完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "导出文件位置: ${YELLOW}$EXPORT_DIR/${NC}"
    echo ""
    echo -e "下一步操作："
    echo -e "1. 将 ${YELLOW}$EXPORT_DIR/${NC} 目录传输到 Debian 虚拟机"
    echo -e "2. 同时传输以下文件到虚拟机："
    echo -e "   - docker-compose.prod.yml"
    echo -e "   - .env.production.template"
    echo -e "   - deploy-to-debian.sh"
    echo -e "3. 在虚拟机上执行: ${YELLOW}sudo bash deploy-to-debian.sh deploy${NC}"
}

# ==================== 函数：导入镜像并部署（在 Debian 上执行）====================
deploy_to_debian() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  开始部署 SkillSpace 到 Debian13${NC}"
    echo -e "${GREEN}========================================${NC}"

    # 检查是否以 root 权限运行
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}错误：请使用 sudo 运行此脚本${NC}"
        exit 1
    fi

    # 步骤 1：安装 Docker 和 Docker Compose（如果未安装）
    echo -e "${YELLOW}[1/6] 检查并安装 Docker...${NC}"
    if ! command -v docker &> /dev/null; then
        echo "Docker 未安装，开始安装..."
        apt-get update
        apt-get install -y docker.io docker-compose
        systemctl start docker
        systemctl enable docker
        echo -e "${GREEN}✓ Docker 安装完成${NC}"
    else
        echo -e "${GREEN}✓ Docker 已安装${NC}"
    fi

    # 步骤 2：导入镜像
    echo -e "${YELLOW}[2/6] 导入 Docker 镜像...${NC}"
    if [ ! -d "$EXPORT_DIR" ]; then
        echo -e "${RED}错误：找不到镜像目录 $EXPORT_DIR${NC}"
        echo "请确保已将镜像文件传输到当前目录"
        exit 1
    fi

    docker load -i "$EXPORT_DIR/frontend.tar"
    docker load -i "$EXPORT_DIR/backend.tar"
    docker load -i "$EXPORT_DIR/celery_worker.tar"
    echo -e "${GREEN}✓ 镜像导入完成${NC}"

    # 步骤 3：配置环境变量
    echo -e "${YELLOW}[3/6] 配置环境变量...${NC}"
    if [ ! -f ".env.production" ]; then
        if [ -f ".env.production.template" ]; then
            cp .env.production.template .env.production
            echo -e "${YELLOW}警告：已从模板创建 .env.production${NC}"
            echo -e "${YELLOW}请编辑 .env.production 文件，修改所有密码和配置！${NC}"
            echo -e "${RED}按任意键继续，或 Ctrl+C 取消...${NC}"
            read -n 1
        else
            echo -e "${RED}错误：找不到 .env.production.template 文件${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ .env.production 已存在${NC}"
    fi

    # 步骤 4：停止旧服务（如果存在）
    echo -e "${YELLOW}[4/6] 停止旧服务...${NC}"
    if [ -f "docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.prod.yml down || true
    fi
    echo -e "${GREEN}✓ 旧服务已停止${NC}"

    # 步骤 5：启动新服务
    echo -e "${YELLOW}[5/6] 启动服务...${NC}"
    docker-compose -f docker-compose.prod.yml up -d
    echo -e "${GREEN}✓ 服务启动完成${NC}"

    # 步骤 6：查看服务状态
    echo -e "${YELLOW}[6/6] 查看服务状态...${NC}"
    sleep 5
    docker-compose -f docker-compose.prod.yml ps

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  部署完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "访问地址："
    echo -e "  前端: ${YELLOW}http://$(hostname -I | awk '{print $1}')${NC}"
    echo -e "  后端API: ${YELLOW}http://$(hostname -I | awk '{print $1}'):8000/api/${NC}"
    echo -e "  RabbitMQ管理: ${YELLOW}http://$(hostname -I | awk '{print $1}'):15672${NC}"
    echo ""
    echo -e "查看日志: ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f${NC}"
}

# ==================== 主函数 ====================
case "$1" in
    export)
        export_images
        ;;
    deploy)
        deploy_to_debian
        ;;
    *)
        echo "使用方法："
        echo "  在 Windows 上导出镜像: bash $0 export"
        echo "  在 Debian 上部署: sudo bash $0 deploy"
        exit 1
        ;;
esac
