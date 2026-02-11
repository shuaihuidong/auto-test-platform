# Zeabur 部署指南

本指南帮助你将自动化测试平台部署到 Zeabur 平台。

## 为什么选择 Zeabur？

- 国内访问速度快（有阿里云节点）
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
2. 选择 "Deploy from GitHub"
3. 授权 Zeabur 访问你的 GitHub 仓库
4. 选择 `auto-test-platform` 仓库

### 4. 部署服务

#### 方式一：使用配置文件（推荐）

项目已包含 `.zeabur.yml` 配置文件，Zeabur 会自动识别并部署：

1. 选择 Region：推荐选择 Hong Kong 或 Singapore（国内访问快）
2. Zeabur 会自动识别配置文件中的服务

#### 方式二：手动添加服务

如果自动识别失败，可以手动添加：

**前端服务**
1. 点击 "Add Service" → "Git" → 选择你的仓库
2. Service Name: `frontend`
3. Root Directory: `frontend`
4. Build Command: 留空（使用 Dockerfile）
5. Start Command: 留空（使用 Dockerfile）

**后端服务**
1. 点击 "Add Service" → "Git" → 选择你的仓库
2. Service Name: `backend`
3. Root Directory: `backend`
4. Build Command: 留空（使用 Dockerfile）
5. Start Command: 留空（使用 Dockerfile）

**RabbitMQ 服务**
1. 点击 "Add Service" → "Prebuilt" → Marketplace
2. 搜索 "RabbitMQ"
3. 选择 `rabbitmq:3.12-management`

### 5. 配置环境变量

在 Zeabur 控制台为每个服务配置环境变量：

#### Backend 环境变量
```
DJANGO_SETTINGS_MODULE=core.settings
SECRET_KEY=your-django-secret-key-here
ALLOWED_HOSTS=*.zeabur.app,localhost
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```

#### Frontend 环境变量
```
NODE_ENV=production
BACKEND_URL=https://your-backend-url.zeabur.app
```

### 6. 域名配置

1. 在 Zeabur 控制台找到每个服务生成的域名
2. 将前端服务的公开 URL 记录下来，这是你的访问地址
3. 配置域名（可选）：可以在 "Networking" → "Custom Domain" 添加自己的域名

### 7. 初始化数据库

部署完成后，需要创建管理员账号：

1. 进入 Zeabur 控制台 → Backend 服务
2. 点击 "Console" 打开终端
3. 运行命令：
```bash
python manage.py createsuperuser
```

4. 按提示输入用户名、邮箱和密码

## 访问你的应用

- **前端页面**: `https://your-frontend.zeabur.app`
- **API 接口**: `https://your-backend.zeabur.app/api/`
- **RabbitMQ 管理界面**: `https://your-rabbitmq.zeabur.app:15672` (默认账号: guest/guest)

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

### Q: 后端和前端无法连接？
A: 检查环境变量 `BACKEND_URL` 是否配置正确，确保使用 Zeabur 分配的内部域名。

### Q: 数据存储问题？
A: Zeabur 的文件系统是临时的，重启后数据会丢失。生产环境建议使用外部数据库服务。

## 成本参考

| 资源 | 免费额度 |
|------|----------|
| CPU | 512 CPU 小时/月 |
| 内存 | 512 MB × 3 个服务 |
| 流量 | 100 GB/月 |

对于演示用途，免费额度完全足够。
