# 安全性改进说明

本文档说明了 v1.4.1 版本中的安全性改进措施。

## 🔐 安全性修复清单

### 1. ✅ Channel层改用Redis

**问题**: 原配置使用内存Channel层，多进程部署时消息会丢失。

**修复**:
- 改用 Redis 作为 Channel 层后端
- 支持多进程和多实例部署
- WebSocket 消息可跨进程共享

**配置要求**:
```bash
# .env 文件
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

**部署要求**:
- 必须安装并启动 Redis 服务
- Docker 部署：使用 `docker-compose.yml` 中的 Redis 服务

---

### 2. ✅ 优化CSRF保护策略

**问题**: 原配置对所有API路径禁用CSRF保护。

**修复**:
- 仅豁免必要的API端点（登录、注册、执行器心跳）
- 其他API端点恢复CSRF保护
- 精确控制豁免范围

**豁免的API路径**:
- `/api/auth/login/` - 用户登录
- `/api/auth/logout/` - 用户登出
- `/api/executor/register/` - 执行器注册
- `/api/executor/heartbeat/` - 执行器心跳

**影响**:
- 前端需要确保在请求中包含 CSRF token（Django默认处理）
- 如遇CSRF错误，检查前端是否正确处理CSRF token

---

### 3. ✅ 密钥管理安全检查

**问题**: 开发环境可能误用默认密钥部署到生产环境。

**修复**:
- 生产环境启动时强制检查密钥安全性
- 禁止使用 `django-insecure-` 开头的默认密钥
- 要求密钥长度至少32个字符

**配置要求**:
```bash
# .env 文件（生产环境必须设置）
DJANGO_SECRET_KEY=your-very-long-and-secure-secret-key-at-least-32-chars

# 生成安全密钥的方法：
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**错误提示**:
- 如果未设置密钥，服务将拒绝启动并提示错误
- 如果密钥不安全，服务将拒绝启动并提示错误

---

### 4. ✅ RabbitMQ密码加密存储

**问题**: RabbitMQ密码以明文存储在数据库中。

**修复**:
- 使用 Fernet 对称加密算法加密存储
- 数据库中存储加密后的密码
- 仅在需要时解密（如返回给执行器客户端）

**配置要求**:
```bash
# .env 文件（生产环境必须设置）
# 生成密钥的命令：
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

RABBITMQ_ENCRYPTION_KEY=<生成的Fernet密钥>
```

**数据迁移**:
- 现有数据库中的明文密码需要迁移
- 使用管理命令加密现有密码：
  ```bash
  # 模拟运行（查看将加密哪些用户）
  python manage.py encrypt_rabbitmq_passwords --dry-run

  # 实际执行加密
  python manage.py encrypt_rabbitmq_passwords
  ```

---

## 📋 部署检查清单

### 开发环境
- [ ] 复制 `.env.example` 为 `.env`
- [ ] 安装并启动 Redis
- [ ] 安装并启动 RabbitMQ
- [ ] 安装 Python 依赖：`pip install -r requirements.txt`
- [ ] 运行数据库迁移：`python manage.py migrate`

### 生产环境
- [ ] 设置安全的 `DJANGO_SECRET_KEY`（至少32字符）
- [ ] 设置 `RABBITMQ_ENCRYPTION_KEY`（使用Fernet生成）
- [ ] 设置 `DEBUG=False`
- [ ] 配置 `DJANGO_ALLOWED_HOSTS`
- [ ] 配置 `CORS_ALLOWED_ORIGINS`
- [ ] 安装并启动 Redis
- [ ] 安装并启动 RabbitMQ
- [ ] 运行数据库迁移
- [ ] **重要**：执行密码加密迁移命令
- [ ] 使用 Daphne 启动服务（支持WebSocket）

---

## 🔧 环境变量完整清单

```bash
# Django 核心配置
DJANGO_SECRET_KEY=<安全密钥，至少32字符>
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DEBUG=False
DJANGO_SETTINGS_MODULE=core.settings_prod

# CORS 配置
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com

# Redis 配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# RabbitMQ 配置
RABBITMQ_HOST=127.0.0.1
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
RABBITMQ_PUBLIC_HOST=<公网IP或域名>  # 远程执行器使用
RABBITMQ_ENCRYPTION_KEY=<Fernet密钥>

# 数据库配置（可选，默认SQLite）
DB_ENGINE=postgresql
DB_NAME=auto_test_platform
DB_USER=postgres
DB_PASSWORD=<数据库密码>
DB_HOST=localhost
DB_PORT=5432
```

---

## 🚨 故障排查

### 问题1: 服务启动失败 - "生产环境必须设置 DJANGO_SECRET_KEY"

**原因**: 未设置环境变量或密钥不安全

**解决**:
```bash
# 生成安全密钥
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 设置环境变量
export DJANGO_SECRET_KEY="生成的密钥"
```

---

### 问题2: WebSocket连接失败

**原因**: Redis未启动或配置错误

**解决**:
```bash
# 检查Redis状态
redis-cli ping

# 启动Redis
redis-server  # Linux
# 或
docker-compose up -d redis  # Docker
```

---

### 问题3: RabbitMQ密码解密失败

**原因**: 加密密钥不匹配或数据未迁移

**解决**:
```bash
# 1. 确认设置了正确的加密密钥
echo $RABBITMQ_ENCRYPTION_KEY

# 2. 运行密码迁移命令
python manage.py encrypt_rabbitmq_passwords --dry-run
python manage.py encrypt_rabbitmq_passwords
```

---

### 问题4: CSRF验证失败

**原因**: API请求缺少CSRF token

**解决**:
- 确保前端在请求头中包含 CSRF token
- Django REST Framework 的 SessionAuthentication 会自动处理
- 检查浏览器是否启用Cookie

---

## 📚 相关文档

- [Django Security](https://docs.djangoproject.com/en/4.2/topics/security/)
- [Channels Redis](https://github.com/django/channels_redis)
- [Cryptography Fernet](https://cryptography.io/en/latest/fernet/)

---

**最后更新**: 2026-03-06
**版本**: v1.4.1
