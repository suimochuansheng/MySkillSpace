#!/bin/bash
# Nginx限流测试脚本
# 用途：测试AI接口、登录接口、普通API的限流效果

echo "=========================================="
echo "Nginx限流测试"
echo "=========================================="
echo ""

# 配置
BASE_URL="${1:-http://localhost}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果记录
TEST_RESULTS=""

# 测试函数
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="$3"
    local data="$4"
    local count="$5"
    local expected_success="$6"
    local expected_429="$7"

    echo "----------------------------------------"
    echo "测试: $name"
    echo "URL: $url"
    echo "请求次数: $count"
    echo "预期成功: $expected_success, 预期429: $expected_429"
    echo "----------------------------------------"

    local success_count=0
    local error_429_count=0
    local other_error_count=0

    for i in $(seq 1 $count); do
        if [ "$method" = "POST" ]; then
            response=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
                -H "Content-Type: application/json" \
                -d "$data" \
                "$url" 2>/dev/null)
        else
            response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
        fi

        if [ "$response" = "200" ] || [ "$response" = "201" ] || [ "$response" = "400" ]; then
            success_count=$((success_count + 1))
            printf "${GREEN}✓${NC} 请求%2d: %s\n" "$i" "$response"
        elif [ "$response" = "429" ]; then
            error_429_count=$((error_429_count + 1))
            printf "${YELLOW}⚠${NC} 请求%2d: %s (限流)\n" "$i" "$response"
        else
            other_error_count=$((other_error_count + 1))
            printf "${RED}✗${NC} 请求%2d: %s (错误)\n" "$i" "$response"
        fi

        # 小延迟，避免瞬间全部发出
        sleep 0.05
    done

    echo ""
    echo "结果统计:"
    echo "  成功响应: $success_count"
    echo "  429限流: $error_429_count"
    echo "  其他错误: $other_error_count"

    # 验证结果
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    local test_passed=true

    # 允许±1的误差
    if [ $success_count -lt $((expected_success - 1)) ] || [ $success_count -gt $((expected_success + 1)) ]; then
        echo -e "${RED}✗ 失败：成功次数不符合预期${NC}"
        test_passed=false
    fi

    if [ $error_429_count -lt $((expected_429 - 1)) ] || [ $error_429_count -gt $((expected_429 + 1)) ]; then
        echo -e "${RED}✗ 失败：429次数不符合预期${NC}"
        test_passed=false
    fi

    if [ "$test_passed" = true ]; then
        echo -e "${GREEN}✓ 测试通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS="${TEST_RESULTS}✅ $name\n"
    else
        echo -e "${RED}✗ 测试失败${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TEST_RESULTS="${TEST_RESULTS}❌ $name\n"
    fi

    echo ""
    sleep 2  # 测试间隔，等待限流恢复
}

# ==================== 测试1：AI接口限流 ====================
# 配置：rate=1r/s, burst=2
# 预期：前3次成功，后面全部429
echo ""
echo "=========================================="
echo "测试1：AI接口限流（最严格）"
echo "配置：rate=1r/s, burst=2"
echo "=========================================="

test_endpoint \
    "AI接口限流" \
    "$BASE_URL/api/ai/chat/" \
    "POST" \
    '{"message":"test"}' \
    10 \
    3 \
    7

# ==================== 测试2：登录接口限流 ====================
# 配置：rate=2r/s, burst=5
# 预期：前7次成功，后面429
echo ""
echo "=========================================="
echo "测试2：登录接口限流（严格）"
echo "配置：rate=2r/s, burst=5"
echo "=========================================="

test_endpoint \
    "登录接口限流" \
    "$BASE_URL/api/auth/login/" \
    "POST" \
    '{"account":"test@example.com","password":"test"}' \
    15 \
    7 \
    8

# ==================== 测试3：普通API限流 ====================
# 配置：rate=20r/s, burst=50
# 预期：前70次成功，后面429
echo ""
echo "=========================================="
echo "测试3：普通API限流（宽松）"
echo "配置：rate=20r/s, burst=50"
echo "=========================================="

test_endpoint \
    "普通API限流" \
    "$BASE_URL/api/users/" \
    "GET" \
    "" \
    100 \
    70 \
    30

# ==================== 测试4：静态资源（不限流） ====================
echo ""
echo "=========================================="
echo "测试4：静态资源（不限流）"
echo "=========================================="

test_endpoint \
    "静态资源不限流" \
    "$BASE_URL/favicon.ico" \
    "GET" \
    "" \
    20 \
    20 \
    0

# ==================== 总结 ====================
echo ""
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo -e "总测试数: $TOTAL_TESTS"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
echo -e "${RED}失败: $FAILED_TESTS${NC}"
echo ""
echo "测试结果详情:"
echo -e "$TEST_RESULTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！限流配置正常工作${NC}"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败，请检查配置${NC}"
    exit 1
fi
