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

# 安装 openssl（用于生成 SSL 证书）
RUN apk add --no-cache openssl

# 自动生成自签名 SSL 证书
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/cert.key \
        -out /etc/nginx/ssl/cert.crt \
        -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost" && \
    chmod 600 /etc/nginx/ssl/cert.key && \
    chmod 644 /etc/nginx/ssl/cert.crt

# 复制构建产物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置文件（支持通过ARG指定）
ARG NGINX_CONFIG=nginx-https.conf.template
COPY ${NGINX_CONFIG} /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
