# Zeabur 部署指南

本指南帮助你将自动化测试平台部署到 Zeabur 平台。

## 为什么选择 Zeabur？

- 国内访问速度快（有香港、新加坡节点）
- 免费额度：$5/月，足够演示使用
- 支持同时部署前端 + 后端 + RabbitMQ
- 自动从 GitHub 部署，推送代码自动更新

## 部署步骤

### 1. 准备工作

确保你的代码已推送到 GitHub 仓库。

### 2. 注册 Zeabur

1. 访问 [https://zeabur.com](https://zeabur.com)
2. 使用 GitHub 账号登录

### 3. 创建新项目

1. 登录后，点击 "Create New Project"
2. 选择 Region：推荐 **Hong Kong** 或 **Singapore**（国内访问快）
3. 给项目命名，如 `auto-test-platform`

### 4. 部署后端服务

1. 在项目页面点击 "Add Service" → "Git"
2. 选择你的 GitHub 仓库
3. 配置服务：
   - **Service Name**: `backend`
   - **Root Directory**: `backend`
   - Zeabur 会自动检测 Dockerfile
4. 点击 "Deploy"

**配置后端环境变量**：
```
DJANGO_SETTINGS_MODULE=core.settings
SECRET_KEY=your-random-secret-key-here
ALLOWED_HOSTS=*.zeabur.app,localhost
```

### 5. 部署前端服务

1. 点击 "Add Service" → "Git"
2. 选择同一个 GitHub 仓库
3. 配置服务：
   - **Service Name**: `frontend`
   - **Root Directory**: `frontend`
   - Zeabur 会自动检测 Dockerfile
4. 点击 "Deploy"

**配置前端环境变量**：
在服务部署后，需要设置后端地址：
1. 在 Zeabur 控制台找到 backend 服务的域名（如 `https://xxx.zeabur.app`）
2. 在 frontend 服务中添加环境变量：
```
BACKEND_URL=https://your-backend-url.zeabur.app
```

### 6. 部署 RabbitMQ 服务

1. 点击 "Add Service" → "Marketplace"
2. 搜索 "RabbitMQ"
3. 选择 `rabbitmq:3.12-management`
4. 点击 "Deploy"

**配置 RabbitMQ**：
```
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=your-strong-password
```

### 7. 配置服务间连接

在后端服务中添加 RabbitMQ 连接环境变量：
```
RABBITMQ_URL=amqp://admin:your-strong-password@rabbitmq:5672/
```

### 8. 初始化数据库

部署完成后，需要创建管理员账号：

1. 进入 Zeabur 控制台 → Backend 服务
2. 点击 "Terminal" 打开终端
3. 运行命令：
```bash
python manage.py createsuperuser
```

4. 按提示输入用户名、邮箱和密码

## 访问你的应用

- **前端页面**: `https://your-frontend.zeabur.app`
- **API 接口**: `https://your-backend.zeabur.app/api/`
- **RabbitMQ 管理界面**: `https://your-rabbitmq.zeabur.app:15672`

## 服务间内部通信

Zeabur 中，服务之间可以通过服务名称直接通信：
- 前端访问后端：`http://backend:8000`
- 后端访问 RabbitMQ：`amqp://admin:password@rabbitmq:5672/`

## 常见问题

### Q: 部署失败怎么办？
A: 查看 Zeabur 控制台的部署日志，根据错误信息排查。常见问题：
- Dockerfile 路径错误
- 端口配置不正确
- 环境变量缺失

### Q: 免费额度够用吗？
A: Zeabur 免费额度为 $5/月，对于演示项目完全足够。超出后可以选择升级或删除服务重新部署。

### Q: 如何更新代码？
A: 直接 push 到 GitHub，Zeabur 会自动检测并重新部署。

### Q: 前端无法连接后端？
A: 检查环境变量 `BACKEND_URL` 是否配置正确，使用 Zeabur 分配的后端域名。

### Q: 数据存储问题？
A: Zeabur 的容器重启后数据会丢失。如需持久化存储，需要在服务设置中添加 "Persistent Volume"。

## 成本参考

| 资源 | 免费额度 |
|------|----------|
| CPU | 512 CPU 小时/月 |
| 内存 | 512 MB × 3 个服务 |
| 流量 | 100 GB/月 |

对于演示用途，免费额度完全足够。
