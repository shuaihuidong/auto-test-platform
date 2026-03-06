# 快速开始 - 安全性配置指南

## 🚀 快速配置（5分钟）

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，设置以下必需项：
```

**开发环境必需配置**:
```bash
# 可使用默认值，但建议设置
DJANGO_SECRET_KEY=your-secret-key-here
RABBITMQ_ENCRYPTION_KEY=ZXhhbXBsZS1kZWZhdWx0LWtleS1mb3ItZGV2LWRvLW5vdC11c2UtaW4tcHJvZHVjdGlvbi1tYWRlLXN1cmUtdG8tY2hhbmdlLWl0
```

**生产环境必需配置**:
```bash
# 生成安全密钥
DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# 生成加密密钥
RABBITMQ_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; import base64; key = Fernet.generate_key(); print(base64.urlsafe_b64encode(key).decode())")

# 其他配置
DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

### 3. 启动依赖服务

**使用 Docker (推荐)**:
```bash
# 在项目根目录
docker-compose up -d
```

**手动安装**:
```bash
# Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                 # macOS

# RabbitMQ
sudo apt-get install rabbitmq-server  # Ubuntu/Debian
brew install rabbitmq                 # macOS
```

### 4. 数据库迁移
```bash
python manage.py migrate
```

### 5. 加密现有密码（如果有）
```bash
# 查看将加密的用户
python manage.py encrypt_rabbitmq_passwords --dry-run

# 执行加密
python manage.py encrypt_rabbitmq_passwords
```

### 6. 启动服务
```bash
# 开发环境
daphne -b 0.0.0.0 -p 8000 core.asgi:application

# 生产环境（使用 Gunicorn + Daphne）
gunicorn core.asgi:application -b 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker
```

---

## ✅ 验证安装

### 1. 检查Redis连接
```bash
redis-cli ping
# 应返回: PONG
```

### 2. 检查RabbitMQ状态
```bash
rabbitmqctl status
# 或访问: http://localhost:15672 (guest/guest)
```

### 3. 测试后端API
```bash
curl http://localhost:8000/api/auth/login/
# 应返回: {"detail":"方法 \"GET\" 不被允许。"}
```

### 4. 测试WebSocket
```javascript
// 浏览器控制台
const ws = new WebSocket('ws://localhost:8000/ws/executor-status/');
ws.onopen = () => console.log('WebSocket 连接成功');
```

---

## 🆘 常见问题

### Q: 启动报错 "生产环境必须设置 DJANGO_SECRET_KEY"
**A**: 设置环境变量或确保 DEBUG=True（开发环境）

### Q: WebSocket连接失败
**A**: 检查Redis是否启动，确认使用daphne而非runserver

### Q: RabbitMQ密码解密失败
**A**: 运行密码加密迁移命令

### Q: CSRF验证失败
**A**: 确保浏览器启用Cookie，前端正确处理CSRF token

---

## 📖 详细文档

- [SECURITY.md](./SECURITY.md) - 完整安全性说明
- [README.md](./README.md) - 项目总览
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 系统架构

---

**快速帮助**:
- 🐛 遇到问题？查看 [SECURITY.md](./SECURITY.md) 的故障排查章节
- 📧 需要支持？提交 GitHub Issue
