# Railway.app 免费部署指南

本文档介绍如何将自动化测试管理平台免费部署到 Railway.app。

> **注意**: Zeabur 现在是 Render 的一部分，功能更强大稳定！

## 🚀 快速开始

### 方案架构

```
┌──────────────────────────────────────────────────────────┐
│                    Railway.app Cloud                        │
│  ┌─────────────────────────────────────────────┐   │
│  │           PostgreSQL (Railway 提供)              │   │
│  └─────────────────────────────────────────────┘   │
│                        ↓                                 │
│  ┌─────────────────────────────────────────────┐   │
│  │              Django Backend (Daphne)               │   │
│  │   • REST API                                      │   │
│  │   • WebSocket                                     │   │
│  └─────────────────────────────────────────────┘   │
│                        ↓                                 │
│  ┌─────────────────────────────────────────────┐   │
│  │              RabbitMQ (Docker)                     │   │
│  │   • 消息队列                                     │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP + WebSocket
                     ▼
              ┌─────────────────────────────────────────────┐
              │              Vercel (前端)              │
              │          Vue 3 SPA                     │
              └─────────────────────────────────────────────┘
```

---

## 📋 部署前准备

### 1. 注册账号

- **Railway**: https://railway.app/
- **GitHub**: 需要用于代码仓库

### 2. 准备代码仓库

将你的代码推送到 GitHub（已完成）

---

## 🐳 后端部署 (Railway)

### 方式一：使用 Docker Compose（推荐）

#### 步骤 1：创建新项目

1. 打开 Railway.app
2. 点击右上角 **"+ New Project"**
3. 选择 **"Deploy from Docker Compose"**
4. 连接你的 GitHub 仓库

#### 步骤 2：选择配置文件

Railway 会自动检测到仓库中的 `railway-compose.yml` 文件：

```yaml
version: "3.8"

services:
  # RabbitMQ 消息队列
  rabbitmq:
    image: rabbitmq:3.12-management
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    volumes:
      - railway-data:/var/lib/rabbitmq

  # Django 后端
  auto-test-backend:
    image: python:3.11-slim
    environment:
      DJANGO_SETTINGS_MODULE: core.settings
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY}
      DEBUG: "False"
      DATABASE_URL: ${Postgres.DATABASE_URL}
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      DJANGO_ALLOWED_HOSTS: "*"
      CORS_ALLOWED_ORIGINS: "https://auto-test-platform.vercel.app,http://localhost:5173"
```

#### 步骤 3：配置环境变量

在 **Variables** 部分添加：

| Key | Value |
|-----|-------|
| `DJANGO_SECRET_KEY` | 点击🎲随机生成 |
| `DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `*` |
| `CORS_ALLOWED_ORIGINS` | `https://auto-test-platform.vercel.app` |

然后点 **Create & Deploy**，等待 3-5 分钟完成。

---

## 🌐 前端部署 (Vercel)

### 步骤 1：导入项目

1. 登录 Vercel: https://vercel.com/new
2. 选择 **"Import Git Repository"**
3. 选择 `auto-test-platform` 仓库

### 步骤 2：配置项目

| 配置项 | 值 |
|--------|------|
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Output Directory | `dist` |

### 步骤 3：设置环境变量

在 Environment Variables 中添加：

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | Railway 后端 URL |

点击 Deploy 完成。

---

## ⚙️ 执行机客户端配置

部署后，配置信息：

| 配置项 | 值 |
|--------|-----|
| **服务器地址** | Railway 后端 URL |
| **RabbitMQ 主机** | Railway 后端 URL (或内部服务名) |
| **RabbitMQ 端口** | `5672` |
| **账号** | 在平台的「账号角色管理」中获取 |

---

## 💰 成本估算

### Railway 免费套餐

| 资源 | 免费额度 |
|--------|----------|
| 运行时间 | $5/月（约 720 小时运行时间） |
| RAM | 512MB |
| CPU | 0.5 vCPU |
| 存储 | 1GB |
| 网络流量 | 100GB/月 |

**评估**：
- ✅ 足够开发/演示使用
- ⚠️ 生产环境建议升级付费版（$5/月起）

### Vercel 免费套餐

| 资源 | 免费额度 |
|--------|----------|
| 构建时间 | 6000 分钟/月 |
| 带宽 | 100GB/月 |
| 部署 | 无限 |

---

## 🔧 常见问题

### Q: 超出免费额度怎么办？

**A**: Railway 会暂停服务，下个月自动恢复。或付费升级。

### Q: WebSocket 连接不上？

**A**: 检查：
1. 后端使用 Daphne 启动（不是 runserver）
2. Vercel 环境变量中 API 地址正确
3. Railway 防火墙允许 WebSocket

### Q: 数据保存在哪？

**A**:
- Railway: PostgreSQL 数据在 Railway 云端
- RabbitMQ: 消息队列在内存中（重启会丢失，可配置持久化）

---

## 📝 部署检查清单

部署完成后，请确认：

- [ ] 后端 API 可以访问（`/api/` 路径返回数据）
- [ ] WebSocket 可以连接（`/ws/` 路径可连接）
- [ ] 前端可以正常加载
- [ ] 可以创建用户并登录
- [ ] 执行机可以连接

---

## 🚀 下一步

部署成功后：

1. **创建超级管理员账号**
2. **绑定自定义域名**（可选）
3. **配置执行机客户端**

---

## 📞 获取帮助

- Railway 文档: https://docs.railway.app/
- Vercel 文档: https://vercel.com/docs
- 项目 Issues: https://github.com/shuaihuidong/auto-test-platform/issues
