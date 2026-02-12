# 多阶段构建 - 前端 Dockerfile for Zeabur
# Stage 1: 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖（使用 npm install 而不是 ci，因为可能没有 lock 文件）
RUN npm install

# 复制源代码
COPY . .

# 构建生产版本（设置环境变量为空字符串以避免变量未定义错误）
RUN npm run build

# Stage 2: 生产阶段
FROM nginx:alpine

# 安装 envsubst 用于环境变量替换
RUN apk add --no-cache gettext

# 复制构建产物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置模板
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# 暴露端口
EXPOSE 80

# 使用 envsubst 替换环境变量后启动 nginx
CMD ["/bin/sh", "-c", "envsubst '$BACKEND_URL' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
