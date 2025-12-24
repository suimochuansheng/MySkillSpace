@echo off
REM ==================== 代码格式化脚本（Windows版本）====================
REM 用途：自动格式化 Python 代码，修复格式问题
REM 使用：format-code.bat

echo =========================================
echo   开始格式化 Python 代码
echo =========================================
echo.

REM 检查并安装依赖工具
echo [1/4] 检查依赖工具...
pip show black >NUL 2>&1 || (
    echo 安装 black...
    pip install black
)

pip show isort >NUL 2>&1 || (
    echo 安装 isort...
    pip install isort
)

pip show flake8 >NUL 2>&1 || (
    echo 安装 flake8...
    pip install flake8
)

echo [OK] 依赖检查完成
echo.

REM 格式化导入语句
echo [2/4] 格式化导入语句 (isort)...
isort --profile black backend/
echo [OK] 导入语句格式化完成
echo.

REM 格式化代码
echo [3/4] 格式化代码 (black)...
black backend/
echo [OK] 代码格式化完成
echo.

REM 检查代码错误
echo [4/4] 检查代码错误 (flake8)...
flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=*/migrations/*,venv,env,__pycache__,*.pyc
echo.

echo =========================================
echo [OK] 代码格式化完成！
echo =========================================
echo.
echo 接下来可以：
echo   1. 查看修改: git diff
echo   2. 提交代码: git add . ^&^& git commit -m "style: 代码格式化"
echo.

pause
