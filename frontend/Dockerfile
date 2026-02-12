# 多阶段构建 - 前端 Dockerfile for Zeabur

# Stage 1: 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建生产版本
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

# 启动 nginx，使用 envsubst 替换环境变量
CMD ["/bin/sh", "-c", "envsubst < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
