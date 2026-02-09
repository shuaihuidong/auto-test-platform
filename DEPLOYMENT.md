# 服务器部署指南

## 环境要求

- Python 3.9+
- Node.js 16+
- Nginx
- (可选) PostgreSQL / MySQL

## 部署步骤

### 1. 后端部署

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，修改以下配置：
# - DJANGO_SECRET_KEY: 生成随机密钥
# - DJANGO_ALLOWED_HOSTS: 设置为你的域名
# - CORS_ALLOWED_ORIGINS: 设置为前端域名
# - CSRF_TRUSTED_ORIGINS: 设置为你的域名

# 生成随机密钥（Linux）
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 数据库迁移
python manage.py migrate --settings=core.settings_prod

# 收集静态文件
python manage.py collectstatic --settings=core.settings_prod --noinput

# 创建超级管理员
python manage.py createsuperuser --settings=core.settings_prod
```

### 2. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 复制环境变量模板
cp .env.example .env.production

# 编辑 .env.production，设置 API 地址
# VITE_API_BASE_URL=https://your-api-domain.com/api

# 构建生产版本
npm run build

# dist 目录即为打包后的文件
```

### 3. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 连接 (重要：执行机客户端需要)
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # 后端静态文件
    location /static {
        alias /path/to/backend/staticfiles;
    }

    # 媒体文件
    location /media {
        alias /path/to/backend/media;
    }
}
```

### 4. 使用 Daphne 运行后端 (支持 WebSocket)

**重要**: 必须使用 Daphne 而不是 Gunicorn/uWSGI，因为执行机客户端需要 WebSocket 连接。

```bash
# 安装 daphne
pip install daphne

# 启动服务
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

### 5. 使用 Systemd 管理服务

创建 `/etc/systemd/system/auto-test-platform.service`:

```ini
[Unit]
Description=Auto Test Platform (ASGI + WebSocket)
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="DJANGO_SETTINGS_MODULE=core.settings_prod"
ExecStart=/usr/local/bin/daphne -b 0.0.0.0 -p 8000 core.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable auto-test-platform
sudo systemctl start auto-test-platform
```

## 配置检查清单

部署前请确认以下配置：

- [ ] 修改 `DJANGO_SECRET_KEY`
- [ ] 设置 `DJANGO_ALLOWED_HOSTS`
- [ ] 配置 `CORS_ALLOWED_ORIGINS`
- [ ] 配置 `CSRF_TRUSTED_ORIGINS`
- [ ] 设置 `DEBUG=False`
- [ ] 配置数据库（如使用 PostgreSQL/MySQL）
- [ ] 运行数据库迁移
- [ ] 收集静态文件
- [ ] 创建超级管理员
- [ ] 配置 Nginx 反向代理
