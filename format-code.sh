#!/bin/bash
# ==================== 代码格式化脚本 ====================
# 用途：自动格式化 Python 代码，修复格式问题
# 使用：bash format-code.sh

set -e  # 遇到错误立即退出

echo "========================================="
echo "  开始格式化 Python 代码"
echo "========================================="

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否安装了所需工具
echo -e "${YELLOW}[1/4] 检查依赖工具...${NC}"

if ! command -v black &> /dev/null; then
    echo "安装 black..."
    pip install black
fi

if ! command -v isort &> /dev/null; then
    echo "安装 isort..."
    pip install isort
fi

if ! command -v flake8 &> /dev/null; then
    echo "安装 flake8..."
    pip install flake8
fi

echo -e "${GREEN}✓ 依赖检查完成${NC}"

# 格式化导入语句
echo -e "${YELLOW}[2/4] 格式化导入语句 (isort)...${NC}"
isort --profile black backend/ || echo "⚠️  isort 警告（可忽略）"
echo -e "${GREEN}✓ 导入语句格式化完成${NC}"

# 格式化代码
echo -e "${YELLOW}[3/4] 格式化代码 (black)...${NC}"
black backend/ || echo "⚠️  black 警告（可忽略）"
echo -e "${GREEN}✓ 代码格式化完成${NC}"

# 检查代码错误
echo -e "${YELLOW}[4/4] 检查代码错误 (flake8)...${NC}"
flake8 backend/ \
    --count \
    --select=E9,F63,F7,F82 \
    --show-source \
    --statistics \
    --exclude=*/migrations/*,venv,env,__pycache__,*.pyc \
    || echo "⚠️  发现代码错误，请修复"

echo ""
echo "========================================="
echo -e "${GREEN}✅ 代码格式化完成！${NC}"
echo "========================================="
echo ""
echo "接下来可以："
echo "  1. 查看修改: git diff"
echo "  2. 提交代码: git add . && git commit -m 'style: 代码格式化'"
echo ""
