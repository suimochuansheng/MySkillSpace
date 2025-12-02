# 使用官方的Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露Django开发服务器端口
EXPOSE 8000

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 运行Django迁移（可以在启动时运行，也可以在构建时运行）
# RUN python manage.py migrate

# 默认启动 Django（Celery 通过 docker-compose 覆盖 command）
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]