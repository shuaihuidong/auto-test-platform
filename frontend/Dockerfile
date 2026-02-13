# 多阶段构建 - 前端 Dockerfile

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

# 复制构建产物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置文件（支持通过ARG指定）
ARG NGINX_CONFIG=nginx.conf.template
COPY ${NGINX_CONFIG} /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
