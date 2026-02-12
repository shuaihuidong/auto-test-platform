# 自动化测试平台 - 部署指南

本文档提供多种部署方案，可根据实际需求选择。

---

## 📑 目录

- [环境要求](#环境要求)
- [方案一：本地开发部署](#方案一本地开发部署)
- [方案二：Render 免费云部署](#方案二render-免费云部署) ⭐ 推荐
- [方案三：Railway 免费云部署](#方案三railway-免费云部署)
- [常见问题](#常见问题)

---

## 环境要求

### 服务端

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 后端运行环境 |
| RabbitMQ | 3.12+ | 消息队列服务 |

### 前端

| 软件 | 版本 | 说明 |
|------|------|------|
| Node.js | 16+ | 前端构建环境 |

---

## 方案一：本地开发部署

适用于开发环境，快速启动所有服务。

### 启动步骤

```bash
# 1. 启动 RabbitMQ
cd D:\AI_project\auto-test-platform
docker-compose up -d

# 2. 启动后端（新终端）
cd backend
python manage.py runserver 0.0.0.0:8000

# 3. 启动前端（新终端）
cd frontend
npm run dev
```

### 访问地址

- 前端：http://localhost:5173 或 http://localhost:3000
- 后端 API：http://localhost:8000/api/
- 后端 WebSocket：ws://localhost:8000/ws/

### 优势

✅ 快速启动
✅ 便于调试
✅ 无网络延迟

### 缺点

❌ 需要本地运行所有服务
❌ 无法分享给他人查看

---

## 方案二：Render 免费云部署 ⭐

**推荐！** 最稳定的免费部署方案，适合演示和小团队使用。

### 免费套餐

| 资源 | 免费额度 |
|--------|----------|
| 运行时间 | 750 小时/月（约 31 天连续运行） |
| RAM | 512MB |
| CPU | 0.5 vCPU |
| 存储 | 不包含（需外部数据库） |
| 网络流量 | 100GB/月 |

### 限制说明

⚠️ 服务 15 分钟无请求会自动休眠
⚠️ 休眠后首次访问需 30-60 秒冷启动
💡 生产环境建议升级付费版（$7/月起）

### 部署架构

```
┌─────────────────────────────────────────────────────┐
│                    Render.com Cloud                          │
│  ┌─────────────────────────────────────────────┐   │
│  │           PostgreSQL (Render 提供)              │   │
│  └─────────────────────────────────────────────┘   │
│                        ↓                                 │
│  ┌─────────────────────────────────────────────┐   │
│  │              Django Backend (Daphne)               │   │
│  │   • REST API                                      │   │
│  │   • WebSocket                                     │   │
│  └─────────────────────────────────────────────┘   │
│                        ↓                                 │
│  ┌─────────────────────────────────────────────┐   │
│  │              RabbitMQ (Worker 服务)             │   │
│  │   • 消息队列                                     │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │ HTTP + WebSocket
                     ▼
              ┌─────────────────────────────────────────────┐
              │              Vercel (前端)              │
              │          Vue 3 SPA                     │
              └─────────────────────────────────────────────┘
```

### 部署步骤

#### 一、后端部署

1. **打开 Render Dashboard**
   访问：https://dashboard.render.com

2. **创建 Web Service**
   - 点击右上角 **"+ New +"**
   - 选择 **"Web Service"**

3. **配置服务**

   | 配置项 | 值/说明 |
   |--------|----------|
   | **Name** | `auto-test-backend` |
   | **Region** | `Oregon (US West)` (保持默认) |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Root Directory** | `backend` ⚠️ 重要 |
   | **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
   | **Start Command** | `daphne -b 0.0.0.0 -p $PORT core.asgi:application` |

4. **配置环境变量**
   在 **Environment** 部分，添加以下变量：

   | Key | Value | 说明 |
   |-----|-------|------|
   | `DJANGO_SETTINGS_MODULE` | `core.settings` |
   | `DJANGO_SECRET_KEY` | 随机字符串，如 `render_secret_2024_abc123` |
   | `DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `*` |
   | `CORS_ALLOWED_ORIGINS` | `https://auto-test-platform.onrender.com,https://auto-test-platform.vercel.app` |

5. **点击 Deploy**
   等待 3-5 分钟部署完成

#### 二、RabbitMQ 部署

1. **创建 Worker Service**
   - 点击 **"+ New +"**
   - 选择 **"Background Worker"**

2. **配置 RabbitMQ**

   | 配置项 | 值/说明 |
   |--------|----------|
   | **Name** | `rabbitmq` |
   | **Image** | `rabbitmq:3.12-management` |
   | **Plan** | `Free` |

3. **点击 Deploy**
   部署后会得到一个 URL，如：`https://rabbitmq-xxxx.onrender.com`

#### 三、更新后端 RabbitMQ 配置

1. 回到后端服务
2. 在 Environment 中添加：

   | Key | Value |
   |-----|-------|
   | `RABBITMQ_HOST` | `rabbitmq-xxxx.onrender.com` (你的 RabbitMQ 服务 URL) |
   | `RABBITMQ_PORT` | `5672` |
   | `RABBITMQ_USER` | `guest` |
   | `RABBITMQ_PASSWORD` | `guest` |

3. 保存后会自动重启后端服务

#### 四、前端部署 (Vercel)

1. **打开 Vercel**
   访问：https://vercel.com/new

2. **导入项目**
   - 选择 **"Import Git Repository"**
   - 搜索并选择 `auto-test-platform`

3. **配置项目**

   | 配置项 | 值 |
   |--------|------|
   | **Project Name** | `auto-test-platform` |
   | **Framework Preset** | `Vite` |
   | **Root Directory** | `frontend` |
   | **Output Directory** | `dist` |

4. **设置环境变量**

   | Key | Value |
   |-----|-------|
   | `VITE_API_BASE_URL` | `https://auto-test-backend.onrender.com/api` |

5. **点击 Deploy**

### 获取部署地址

部署完成后，你会得到以下地址：

| 服务 | URL 示例 | 用途 |
|------|----------|------|
| **后端 API** | `https://auto-test-backend.onrender.com/api` | 前端调用 |
| **后端 WebSocket** | `wss://auto-test-backend.onrender.com/ws/` | 实时通信 |
| **前端** | `https://auto-test-platform.vercel.app` | 用户访问 |

### 验证部署

1. **测试 API**
   访问 `https://auto-test-backend.onrender.com/api/`
   应返回 `{"detail":"方法不允许"}` 或类似 JSON 响应

2. **创建超级管理员**
   - 在 Render Dashboard → 后端服务
   - 点击 **"Shell"** 标签
   - 运行：`python manage.py createsuperuser`

3. **测试登录**
   - 打开前端地址
   - 使用刚创建的账号登录

4. **测试 WebSocket**
   - 打开浏览器开发者工具（F12）
   - Network 标签，过滤 `WS` 或 `WS`
   - 刷新页面，查看是否有 WebSocket 连接

---

## 方案三：Railway 免费云部署

**注意**：Railway 现在需要信用卡验证才能注册。

### 免费套餐

| 资源 | 免费额度 |
|--------|----------|
| 运行时间 | $5/月（约 720 小时运行时间） |
| RAM | 512MB |
| CPU | 0.5 vCPU |
| 存储 | 1GB |
| 网络流量 | 100GB/月 |

### 限制说明

💡 用完免费额度后会自动暂停
💡 下月1号自动重置
💡 生产环境建议升级付费版（$5/月起）

### 部署步骤

1. **打开 Railway**
   访问：https://railway.app/

2. **创建新项目**
   - 选择 **"Deploy from Docker Compose"**
   - 连接 GitHub 仓库

3. **选择配置文件**
   - 选择 `railway-compose.yml`
   - 文件内容：

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
      DJANGO_ALLOWED_HOSTS: "*"
      CORS_ALLOWED_ORIGINS: "https://auto-test-platform.vercel.app"
```

4. **配置环境变量**

   | Key | Value |
   |-----|-------|
   | `DJANGO_SECRET_KEY` | 随机字符串 |
   | `DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `*` |
   | `CORS_ALLOWED_ORIGINS` | `https://auto-test-platform.vercel.app` |

5. **点击 Deploy**
   等待 3-5 分钟完成

### 验证部署

部署完成后，检查服务状态：
- ✅ rabbitmq ● Running
- ✅ auto-test-backend ● Running
- ✅ postgresql ● Running

获取后端 URL（点击服务查看）：
- `https://auto-test-backend.up.railway.app`

---

## 常见问题

### Q: 免费额度用完了怎么办？

**A:** 服务会自动暂停，下个月1号自动恢复。或升级付费版。

---

### Q: WebSocket 连接不上？

**A:** 检查以下几点：
1. 后端使用 Daphne 启动（不是 runserver）
2. 环境变量中 API 地址正确
3. 平台防火墙允许 WebSocket 连接

---

### Q: 服务一直休眠怎么办？

**A:**
- **Render**: 升级付费版（$7/月起）
- **Railway**: 无法避免，这是按月计费的

---

### Q: 数据存储在哪里？

**A:**
- **本地部署**: SQLite 文件在 `backend/db.sqlite3`
- **Render**: PostgreSQL 在云端（自动创建）
- **Railway**: PostgreSQL 在云端（自动创建）

---

### Q: 如何创建超级管理员？

**A:**
- **本地部署**: `python manage.py createsuperuser`
- **Render**: Dashboard → 服务 → Shell → 运行命令
- **Railway**: Dashboard → 服务 → Shell → 运行命令

---

### Q: 执行机客户端如何配置？

**A:** 给执行机用户的配置信息：

| 配置项 | 值 |
|--------|-----|
| **服务器地址** | 你的部署 URL（如 `https://auto-test-backend.onrender.com`） |
| **RabbitMQ 主机** | 同服务器地址或 RabbitMQ 服务地址 |
| **RabbitMQ 端口** | `5672` |
| **账号密码** | 在平台的「账号角色管理」中点击「RabbitMQ配置」获取 |

---

## 部署方案对比

| 特性 | 本地部署 | Render | Railway |
|------|----------|--------|--------|
| **成本** | 免费 | 免费 | $5/月或免费 |
| **难度** | ⭐ 简单 | ⭐⭐⭐ 中等 | ⭐⭐ 中等 |
| **WebSocket** | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| **数据库** | SQLite | PostgreSQL(云) | PostgreSQL(云) |
| **RabbitMQ** | Docker本地 | Worker服务 | Docker服务 |
| **稳定性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **访问速度** | 最快 | 快 | 快 |
| **休眠问题** | 无 | 15分钟无活动休眠 | 无 |
| **推荐场景** | 本地开发 | 演示/生产 | 演示/测试 |

**推荐排序**：本地 > Render > Railway

---

## 更新日志

### v1.4.1 (2026-02-12) - 部署文档更新

- 整合所有部署方案到统一文档
- 添加详细的 Render 部署步骤
- 添加常见问题解答
- 删除冗余的部署文档
- 优化部署方案对比表格
