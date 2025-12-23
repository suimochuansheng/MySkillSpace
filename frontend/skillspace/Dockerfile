# ==================== 第一阶段：构建阶段 ====================
# 使用 Node.js 官方镜像作为构建环境（Vite 7 需要 Node.js 20+）
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json（如果存在）
# 为什么先复制这两个文件？因为可以利用 Docker 缓存层！
# 只要依赖不变，这一层就不会重新构建
COPY package*.json ./

# 安装项目依赖
# --legacy-peer-deps: 解决某些包的依赖冲突问题
RUN npm install --legacy-peer-deps

# 复制所有源代码到容器中
COPY . .

# 执行构建命令
# 这会生成 dist/ 目录，里面是编译后的静态文件
RUN npm run build

# ==================== 第二阶段：运行阶段 ====================
# 使用 Nginx 作为 Web 服务器
FROM nginx:1.25-alpine

# 从构建阶段复制编译好的文件到 Nginx 的静态文件目录
# /app/dist 是第一阶段构建出来的产物
# /usr/share/nginx/html 是 Nginx 默认的静态文件目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义的 Nginx 配置文件（稍后我们会创建）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露 80 端口（HTTP）
EXPOSE 80

# 启动 Nginx
# daemon off; 让 Nginx 在前台运行，否则容器会立即退出
CMD ["nginx", "-g", "daemon off;"]
