# Zeabur 部署指南

本指南帮助你将自动化测试平台部署到 Zeabur 平台（2026 最新版）。

## 为什么选择 Zeabur？

- 国内访问速度快（有香港、新加坡节点）
- 免费额度：$5/月，足够演示使用
- 支持同时部署前端 + 后端 + RabbitMQ
- 自动从 GitHub 部署，推送代码自动更新
- AI Agent 辅助部署，更简单快捷

## 部署步骤

### 步骤一：注册并验证账户

1. 访问 [https://zeabur.com](https://zeabur.com)

2. 点击 **"通过电子邮件继续"**，填写你的邮箱

3. 检查邮箱，点击 Zeabur 发送的 **"登录"** 链接

4. 完成账户验证（三选一）：
   - **手机号码验证**（推荐，大部分地区支持）
   - **预存使用额度**（$10 起充，不会自动扣款）
   - **绑定信用卡**（仅作验证，订阅前不会扣款）

### 步骤二：创建新项目

1. 登录后，点击右上角 **"创建新项目"** 或中央的 **"创建项目"** 按钮

2. 选择 Region：
   - **Hong Kong**（香港）- 国内访问最快
   - **Singapore**（新加坡）- 国内访问较快

3. 给项目命名，如 `auto-test-platform`

4. 点击 **"创建"** 完成项目创建

### 步骤三：部署后端服务

1. 在项目页面点击 **"添加服务"** → **"Git"**

2. 首次使用需要绑定 GitHub，点击 **"连接 GitHub"**

3. 等待约 1 分钟后，搜索并选择你的 GitHub 仓库（`shuaihuidong/auto-test-platform`）

4. Zeabur 会**自动分析代码**并选择部署方式：
   - Root Directory: `backend`
   - Zeabur 自动检测到 Dockerfile

5. 点击 **"部署"** 开始构建

**配置后端环境变量**（部署后在服务设置中添加）：

| Key | Value |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `core.settings` |
| `SECRET_KEY` | 随机生成的密钥 |
| `ALLOWED_HOSTS` | `*.zeabur.app,localhost` |

### 步骤四：部署前端服务

1. 点击 **"添加服务"** → **"Git"**

2. 选择同一个 GitHub 仓库

3. 配置：
   - Root Directory: `frontend`
   - Zeabur 自动检测到 Dockerfile

4. 点击 **"部署"**

**配置前端环境变量**：

部署后需要设置后端地址：

1. 在 Zeabur 控制台找到 backend 服务的域名（如 `https://xxx.zeabur.app`）

2. 在 frontend 服务 → **"环境变量"** 中添加：

| Key | Value |
|-----|-------|
| `BACKEND_URL` | `https://your-backend-url.zeabur.app` |

### 步骤五：部署 RabbitMQ 服务

1. 点击 **"添加服务"** → **"市场"**（Marketplace）

2. 搜索 **"RabbitMQ"**

3. 选择 `rabbitmq:3.12-management`

4. 点击 **"部署"**

**配置 RabbitMQ**（可选，建议修改默认密码）：

| Key | Value |
|-----|-------|
| `RABBITMQ_DEFAULT_USER` | `admin` |
| `RABBITMQ_DEFAULT_PASS` | 设置强密码 |

### 步骤六：配置服务间连接

在后端服务的环境变量中添加 RabbitMQ 连接信息：

| Key | Value |
|-----|-------|
| `RABBITMQ_HOST` | `rabbitmq`（服务名称） |
| `RABBITMQ_PORT` | `5672` |
| `RABBITMQ_USER` | 设置的用户名 |
| `RABBITMQ_PASSWORD` | 设置的密码 |
| `RABBITMQ_VHOST` | `/` |

或使用连接字符串格式：
```
RABBITMQ_URL=amqp://admin:password@rabbitmq:5672/
```

### 步骤七：初始化数据库

部署完成后，创建管理员账号：

1. 进入 Zeabur 控制台 → **Backend 服务**

2. 点击 **"终端"**（Terminal）标签

3. 运行命令：
```bash
python manage.py createsuperuser
```

4. 按提示输入用户名、邮箱和密码

## 访问你的应用

部署完成后，在 Zeabur 控制台可以看到各服务的访问地址：

| 服务 | URL 示例 |
|------|----------|
| **前端页面** | `https://your-frontend.zeabur.app` |
| **API 接口** | `https://your-backend.zeabur.app/api/` |
| **RabbitMQ 管理界面** | `https://your-rabbitmq.zeabur.app:15672` |

## 使用 AI Agent 部署（可选）

Zeabur 的 AI 助理可以让你用自然语言快速部署服务：

1. 点击导航栏的 **"Agent"** 进入 AI 助理界面

2. 用中文描述你的需求，例如：
   > "帮我部署一个 Django 测试平台，需要前端、后端和 RabbitMQ 服务"

3. AI 会自动分析并为你配置好所有服务

4. 如果遇到问题，也可以向 AI 寻求帮助

## 服务间内部通信

Zeabur 中，同一项目的服务之间可以通过服务名称直接通信：

- 前端访问后端：`http://backend:8000`
- 后端访问 RabbitMQ：`amqp://admin:password@rabbitmq:5672/`

## 常见问题

### Q: 部署失败怎么办？

**A:** 查看 Zeabur 控制台的部署日志，根据错误信息排查。常见问题：
- Dockerfile 路径或配置错误
- 环境变量缺失或配置错误
- 依赖安装失败

### Q: 免费额度够用吗？

**A:** Zeabur 免费额度为 $5/月，对于演示和小型项目完全足够。超出后可以选择升级或删除服务重新部署。

### Q: 如何更新代码？

**A:** 直接 push 到 GitHub，Zeabur 会自动检测并重新部署对应的服务。

### Q: 前端无法连接后端？

**A:** 检查以下几点：
1. 环境变量 `BACKEND_URL` 是否配置正确
2. 使用 Zeabur 分配的后端域名（不是服务名称）
3. CORS 设置是否包含前端域名

### Q: 数据存储问题？

**A:** Zeabur 的容器重启后部分数据会丢失。如需持久化存储：
1. 进入服务设置 → **"持久化存储"**
2. 添加需要持久化的路径（如 `/app/db`）

### Q: 如何绑定自己的域名？

**A:**
1. 进入项目 → **"域名"**
2. 点击 **"绑定域名"**
3. 输入你的域名并按提示配置 DNS
4. 等待约 30 秒，Zeabur 会自动处理 HTTPS

## 成本参考

| 资源 | 免费额度 |
|------|----------|
| CPU | 512 CPU 小时/月 |
| 内存 | 512 MB × 3 个服务 |
| 流量 | 100 GB/月 |
| 存储 | 按需计费 |

对于演示和个人项目，免费额度完全足够。

## 部署检查清单

部署前确认：

- [ ] 代码已推送到 GitHub
- [ ] Dockerfile 存在于 `backend/` 和 `frontend/` 目录
- [ ] 已完成 Zeabur 账户验证

部署后确认：

- [ ] 后端服务状态为 ● Running
- [ ] 前端服务状态为 ● Running
- [ ] RabbitMQ 服务状态为 ● Running
- [ ] 环境变量已正确配置
- [ ] 已创建管理员账号
- [ ] 前端可以正常访问并登录

---

**文档更新时间：2026-02**
**Zeabur 官方文档：https://zeabur.com/docs**
