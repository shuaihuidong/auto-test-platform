# 自动化测试管理平台

<div align="center">

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Django](https://img.shields.io/badge/Django-4.2.7-green)
![Vue](https://img.shields.io/badge/Vue-3.3.8-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

一个基于 Vue3 + Django 的自动化测试管理平台，通过可视化拖拉拽方式创建和管理多类型测试脚本。

**核心特性**: 消息队列架构 | 独立执行器 | 可视化脚本编辑 | 多框架支持 | RabbitMQ用户管理

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用说明](#使用说明) • [部署文档](#生产环境部署)

</div>

## 功能特性

| 功能 | 描述 |
|------|------|
| 🎨 **可视化脚本编辑器** | 拖拉拽方式创建测试步骤，支持可视化/JSON 双模式编辑，8大类50+步骤类型 |
| 🔧 **多框架支持** | Selenium、Playwright、Appium、HttpRunner |
| 📊 **丰富的测试报告** | ECharts 图表展示，HTML/PDF 报告导出，实时执行状态 |
| 🧩 **模块化复用** | 将常用步骤保存为模块，提高脚本复用性 |
| 📈 **参数化测试** | 支持数据驱动，批量执行测试 |
| ⚡ **并发执行** | 支持多任务并发执行，提高测试效率 |
| 🚦 **实时执行控制** | WebSocket 实时推送执行状态，支持手动停止 |
| 👥 **权限分级管理** | 四级角色权限，灵活控制访问 |
| 🔌 **变量管理** | 项目级/脚本级变量，支持敏感数据加密 |
| 📦 **独立执行器** | 独立的执行器客户端，支持远程部署，PyQt6 GUI |
| 🔄 **消息队列架构** | RabbitMQ 实现任务分发，支持多执行机负载均衡 |
| 🔐 **RabbitMQ用户管理** | 超级管理员可创建/管理执行机专用MQ账号，支持远程连接 |

## 技术栈

| 层级 | 技术选择 | 版本 |
|------|----------|------|
| 前端 | Vue 3 + Vite + TypeScript + Ant Design Vue | 3.3.8 / 5.0.2 |
| 后端 | Django + Django REST Framework + Channels | 4.2.7 / 3.14.0 |
| WebSocket | Daphne (ASGI服务器) | - |
| 消息队列 | RabbitMQ + Pika | 3.12+ / 1.3.2 |
| 数据库 | SQLite (支持 PostgreSQL/MySQL) | 3 |
| 测试框架 | Selenium / Playwright / Appium / HttpRunner | 4.15.2 / 1.40.0 / 3.1.1 |

## 支持的脚本类型

| 类型 | 说明 | 支持框架 |
|------|------|----------|
| **Web自动化** | Web 应用 UI 自动化测试 | Selenium, Playwright |
| **移动端自动化** | 移动应用 UI 自动化测试 | Appium |
| **API接口测试** | HTTP/HTTPS 接口测试 | HttpRunner |

## 权限分级

| 角色 | 等级 | 权限说明 |
|------|------|----------|
| **超级管理员** (super_admin) | 4 | 全部权限 + 管理用户 + 系统设置 + **RabbitMQ用户管理** |
| **管理员** (admin) | 3 | 查看、创建、更新、删除、执行测试 |
| **测试人员** (tester) | 2 | 查看、创建脚本、执行测试 |
| **访客** (guest) | 1 | 仅查看权限 |

## 项目结构

```
auto-test-platform/
├── backend/                    # Django 后端
│   ├── core/                   # 核心配置
│   │   ├── settings.py         # 主配置文件 (含RabbitMQ配置)
│   │   ├── urls.py             # URL路由配置
│   │   ├── asgi.py             # ASGI配置 (WebSocket)
│   │   └── wsgi.py             # WSGI配置
│   ├── apps/                   # 应用模块
│   │   ├── users/              # 用户管理 (权限分级、认证、RabbitMQ用户管理)
│   │   │   ├── models.py       # User模型 (role字段)
│   │   │   ├── permissions.py  # 权限控制
│   │   │   ├── serializers.py  # 数据序列化
│   │   │   └── views.py        # 视图逻辑 (含RabbitMQ用户管理API)
│   │   ├── projects/           # 项目管理
│   │   ├── scripts/            # 脚本管理 + 数据源管理
│   │   │   ├── models.py       # Script, DataSource, ApiTestConfig
│   │   │   └── urls.py         # API路由
│   │   ├── plans/              # 计划管理
│   │   ├── executions/         # 执行管理
│   │   │   ├── consumers.py    # WebSocket消费者
│   │   │   └── models.py       # Execution模型 (含display_id自增)
│   │   ├── reports/            # 报告管理
│   │   │   ├── generators.py   # 报告生成器
│   │   │   └── models.py       # Report模型
│   │   ├── drivers/            # 驱动管理
│   │   ├── executors/          # 执行器管理 (分组/标签)
│   │   │   ├── consumers.py    # WebSocket消费者
│   │   │   ├── heartbeat.py    # HTTP心跳和注册API
│   │   │   └── routing.py      # WebSocket路由
│   │   └── scheduler/          # 调度器
│   ├── services/               # 服务层
│   │   ├── message_queue.py    # RabbitMQ 发布者服务
│   │   └── task_distributor.py # 任务分发服务
│   ├── engine/                 # 测试引擎
│   │   └── appium_engine.py    # Appium引擎
│   ├── media/                  # 媒体文件 (截图等)
│   ├── reports/                # 测试报告存储
│   ├── manage.py               # Django 管理脚本
│   └── requirements.txt        # Python 依赖
│
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── api/                # API 调用封装
│   │   │   ├── request.ts      # Axios 封装
│   │   │   ├── user.ts         # 用户 API
│   │   │   ├── project.ts      # 项目 API
│   │   │   ├── script.ts       # 脚本 API
│   │   │   ├── execution.ts    # 执行 API
│   │   │   └── executor.ts     # 执行器 API
│   │   ├── components/         # 公共组件
│   │   │   └── ScriptEditor/   # 可视化脚本编辑器
│   │   ├── store/              # Pinia 状态管理
│   │   ├── router/             # 路由配置
│   │   ├── types/              # TypeScript 类型定义
│   │   ├── layout/             # 布局组件
│   │   ├── config/             # 配置文件
│   │   ├── utils/              # 工具函数
│   │   ├── styles/             # 样式文件
│   │   └── views/              # 页面视图
│   │       ├── Login.vue           # 登录页
│   │       ├── ProjectList.vue     # 项目列表
│   │       ├── ProjectDetail.vue   # 项目详情
│   │       ├── ScriptList.vue      # 脚本列表
│   │       ├── ScriptEdit.vue      # 脚本编辑
│   │       ├── PlanManage.vue      # 测试计划
│   │       ├── ExecutionList.vue   # 执行记录
│   │       ├── ReportView.vue      # 测试报告
│   │       ├── ExecutorManage.vue  # 执行器管理
│   │       ├── VariableManage.vue  # 变量管理
│   │       ├── UserManage.vue      # 用户管理
│   │       ├── AccountRoleManage.vue # 账号角色管理 (含RabbitMQ用户管理)
│   │       ├── DriverCenter.vue    # 驱动中心
│   │       └── HelpCenter.vue      # 帮助中心
│   ├── index.html              # 入口 HTML
│   └── package.json            # Node 依赖
│
├── executor-client/            # 执行器客户端 (PyQt6独立应用)
│   ├── main.py                 # 主入口
│   ├── config.py               # 配置管理
│   ├── executor.py             # 执行器核心逻辑
│   ├── task_manager.py         # 任务管理器 (旧版WebSocket)
│   ├── task_manager_v2.py      # 新任务管理器 (MQ + HTTP)
│   ├── websocket_client.py     # WebSocket 通信
│   ├── message_queue_client.py # RabbitMQ 消费者
│   ├── gui/                    # PyQt6 GUI 界面
│   │   ├── main_window.py      # 主窗口
│   │   └── config_wizard.py    # 配置向导
│   ├── build.py                # 打包脚本
│   ├── requirements.txt        # Python 依赖
│   └── 使用说明.md             # 使用说明文档
│
├── docker-compose.yml          # Docker Compose 配置
├── setup_rabbitmq.ps1          # Windows RabbitMQ 安装脚本
├── DEPLOYMENT.md               # 详细部署文档
├── MQ_SUMMARY.md               # 消息队列架构总结
├── RABBITMQ_*.md               # RabbitMQ 相关文档
└── README.md                   # 项目说明 (本文件)
```

## 系统架构

### 通信架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Web 浏览器                            │
│                    (Vue.js 前端应用)                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP + WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Django 后端                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              REST API (Django REST Framework)        │   │
│  │  /api/auth/  /api/users/  /api/projects/            │   │
│  │  /api/scripts/  /api/executions/  /api/reports/     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            WebSocket (Channels + Daphne)            │   │
│  │  /ws/executor-status/  →  Web UI 状态展示           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          TaskDistributor (任务分发服务)             │   │
│  │    扫描待执行任务 → 选择可用执行机 → 发布到MQ       │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       RabbitMQ 用户管理 (仅超级管理员)              │   │
│  │  创建用户  列表展示  删除用户  修改密码              │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP POST (发布任务)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RabbitMQ 消息队列                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              交换机: executor_tasks                  │   │
│  │  队列: executor.{uuid} (每执行机专属队列)            │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ 消费任务
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   执行器客户端 (PyQt6)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          MessageQueueClient (RabbitMQ消费者)        │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               Executor (执行引擎)                   │   │
│  │  Selenium | Playwright | Appium | HttpRunner       │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          HTTP 心跳上报 (30秒一次)                    │   │
│  │  POST /api/executor/heartbeat/                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 数据流说明

**任务分发流程**:
1. 用户在Web UI点击"执行测试"
2. 前端调用 `POST /api/executions/` 创建执行记录
3. TaskDistributor 后台服务扫描待分配任务
4. 根据执行机状态选择可用执行机
5. 将任务发布到RabbitMQ (routing_key: `executor.{uuid}`)
6. 执行机从专属队列消费任务并执行
7. 执行结果通过HTTP POST上报到平台

**心跳上报流程**:
1. 执行机启动后每30秒发送HTTP心跳
2. 携带系统资源信息 (CPU/内存/磁盘)
3. 平台更新执行机状态和最后心跳时间
4. 超过一定时间未收到心跳则标记为离线

**状态展示流程**:
1. Web UI 连接 `/ws/executor-status/`
2. 平台通过 channel_layer 广播执行机状态变化
3. 前端实时接收状态更新并展示

**RabbitMQ用户管理流程**:
1. 超级管理员在「账号角色管理」页面创建RabbitMQ用户
2. 平台通过RabbitMQ HTTP API创建用户并设置权限
3. 用户名/密码提供给执行机用户用于配置
4. 执行机使用专用账号连接RabbitMQ（支持远程）

## API 端点

### 认证相关

| 端点 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/auth/login/` | POST | 用户登录 | 公开 |
| `/api/auth/logout/` | POST | 用户登出 | 认证用户 |

### 用户管理

| 端点 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/users/` | GET/POST | 用户列表/创建 | 管理员+ |
| `/api/users/{id}/` | PUT/DELETE | 更新/删除用户 | 管理员+ |
| `/api/users/me/` | GET | 获取当前用户信息 | 认证用户 |
| `/api/users/permissions/` | GET | 获取当前用户权限 | 认证用户 |
| `/api/users/{id}/set_role/` | POST | 设置用户角色 | 超级管理员 |
| `/api/users/{id}/reset_password/` | POST | 重置用户密码 | 管理员+ |
| `/api/users/change_password/` | POST | 修改自己的密码 | 认证用户 |
| `/api/users/role_list/` | GET | 获取角色列表 | 管理员+ |
| `/api/users/role_users/{role}/` | GET | 获取指定角色的用户 | 管理员+ |

### RabbitMQ用户管理（超级管理员专属）

| 端点 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/users/create_rabbitmq_user/` | POST | 创建RabbitMQ用户 | 超级管理员 |
| `/api/users/list_rabbitmq_users/` | GET | 列出RabbitMQ用户 | 超级管理员 |
| `/api/users/delete_rabbitmq_user/` | POST/DELETE | 删除RabbitMQ用户 | 超级管理员 |
| `/api/users/update_rabbitmq_user_password/` | POST | 修改RabbitMQ用户密码 | 超级管理员 |

### 项目与脚本

| 端点 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/projects/` | GET/POST | 项目列表/创建 | 测试人员+ |
| `/api/scripts/` | GET/POST | 脚本列表/创建 | 测试人员+ |
| `/api/scripts/{id}/` | PUT/DELETE | 更新/删除脚本 | 管理员+ |
| `/api/plans/` | GET/POST | 测试计划列表/创建 | 测试人员+ |
| `/api/executions/` | GET/POST | 执行记录列表/创建执行 | 测试人员+ |
| `/api/executions/{id}/stop/` | POST | 停止执行 | 认证用户 |

### 执行器管理

| 端点 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/executor/register/` | POST | 执行机注册 | 公开 |
| `/api/executor/heartbeat/` | POST | 执行机心跳上报 | 公开 |
| `/ws/executor-status/` | WebSocket | 执行机状态监听 | 认证用户 |

### 其他

| 端点 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/reports/` | GET | 测试报告 | 认证用户 |
| `/api/drivers/` | GET | 驱动列表 | 认证用户 |

## 快速开始

### 环境要求

| 软件 | 版本要求 |
|------|----------|
| Python | 3.9+ |
| Node.js | 16+ |
| RabbitMQ | 3.12+ (消息队列) |

### 1. 安装 RabbitMQ (消息队列)

**方式一: Docker (推荐)**
```bash
cd auto-test-platform
docker-compose up -d
```

**方式二: Windows 快速安装**
```powershell
# 以管理员身份运行 PowerShell
.\setup_rabbitmq.ps1
```

**方式三: 手动安装**
1. 下载安装 Erlang/OTP
2. 下载安装 RabbitMQ
3. 启用管理插件: `rabbitmq-plugins enable rabbitmq_management`
4. 启动服务: `rabbitmq-service start`

**验证安装**: 访问 http://localhost:15672 (用户名/密码: guest/guest)

### 2. 后端启动

```bash
cd backend

# 安装依赖 (包含 pika 用于 RabbitMQ)
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员 (可选)
python create_admin.py

# 启动后端服务 (使用 daphne 支持 WebSocket)
daphne -b 0.0.0.0 -p 8000 core.asgi:application

# 或者在 Windows 上双击: 启动服务器.bat
```

**环境变量配置** (可选):
```bash
# 设置 RabbitMQ 连接信息
export RABBITMQ_HOST=127.0.0.1
export RABBITMQ_PORT=5672
export RABBITMQ_USER=guest
export RABBITMQ_PASSWORD=guest
```

**重要提示**:
- 必须使用 `daphne` 启动服务器以支持 WebSocket 连接
- `runserver` 不支持 WebSocket，Web UI 将无法接收实时状态

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 即可使用平台。

### 4. 执行器客户端启动

#### 本地执行机（与服务端同电脑）

如果执行机和服务器在同一台电脑上，可以使用默认的 `guest` 账号：

```bash
cd executor-client

# 安装依赖
pip install -r requirements.txt

# 启动 GUI 客户端
python main.py
```

配置向导中填写：
- 服务器地址: `http://127.0.0.1:8000`
- RabbitMQ地址: `127.0.0.1`
- 用户名: `guest`
- 密码: `guest`
- 执行机名称: 自定义名称 (如 "本地执行机-01")

#### 远程执行机（与服务端不同电脑）

由于 RabbitMQ 的 `guest` 账号只允许本地连接，远程执行机需要使用专用的 RabbitMQ 用户：

1. **创建 RabbitMQ 用户**：
   - 登录平台（需超级管理员权限）
   - 进入「账号角色管理」→「角色管理」标签页
   - 在「RabbitMQ 用户管理」区域点击「创建 RabbitMQ 用户」
   - 填写用户名（如 `executor-remote-01`）和密码
   - 点击创建，系统会生成用户并显示凭证信息

2. **配置远程执行机**：
   ```bash
   cd executor-client
   python main.py
   ```

   配置向导中填写：
   - 服务器地址: `http://[服务器IP]:8000`（填写实际IP）
   - RabbitMQ地址: `[服务器IP]`（填写实际IP）
   - 用户名: 刚创建的用户名（如 `executor-remote-01`）
   - 密码: 创建时设置的密码
   - 执行机名称: 自定义名称

### 5. 验证安装

1. **检查 RabbitMQ**: 访问 http://localhost:15672，确认服务正常运行
2. **启动后端**: 看到 "Starting server at ..." 表示成功
3. **启动前端**: 访问 http://localhost:5173，看到登录页面
4. **启动执行器**: 配置完成后连接服务器，在平台执行器管理中看到在线状态

## 默认测试账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 超级管理员 |
| admin2 | admin123 | 管理员 |
| tester1 | test123 | 测试人员 |
| guest1 | guest123 | 访客 |

## 使用说明

### RabbitMQ用户管理（超级管理员专属）

当执行机部署在远程服务器时，需要使用专用的RabbitMQ用户账号进行连接。

**创建用户**：
1. 使用超级管理员账号登录平台
2. 进入「账号角色管理」页面
3. 切换到「角色管理」标签页
4. 在「RabbitMQ 用户管理」区域点击「创建 RabbitMQ 用户」
5. 填写用户名和密码，选择标签（management用于访问管理插件）
6. 创建成功后，将凭证信息提供给执行机用户

**管理用户**：
- **查看列表**：进入「角色管理」标签页自动加载，或点击「刷新」按钮
- **删除用户**：点击用户行的「删除」按钮
- **修改密码**：点击用户行的「改密」按钮

**重要说明**：
- `guest` 账号只能用于本地连接（localhost）
- 远程执行机必须使用专用的RabbitMQ用户
- 创建的用户默认拥有完整权限（configure/write/read 为 `.*`）

### 创建测试脚本流程

```
1. 创建项目 → 选择项目类型 (Web/移动端/API)
2. 新建脚本 → 选择测试框架 (Selenium/Playwright/Appium/HttpRunner)
3. 编辑步骤 → 从左侧拖拽步骤到画布
4. 配置参数 → 在右侧属性面板配置步骤参数
5. 保存脚本 → 保存脚本
6. 运行测试 → 点击运行按钮执行
7. 查看报告 → 查看执行结果和统计图表
```

### 步骤类型说明

| 分类 | 步骤 | 说明 |
|------|------|------|
| **页面控制** | 打开页面 | 导航到指定 URL |
| | 滚动页面 | 滚动到顶部/底部/自定义位置 |
| | 切换窗口/框架 | 切换到指定窗口或 iframe |
| | 刷新/后退/前进 | 浏览器导航操作 |
| **交互操作** | 点击/双击/右键 | 鼠标点击操作 |
| | 输入文本 | 在输入框输入文本 |
| | 清空输入 | 清空输入框内容 |
| | 下拉选择 | 选择下拉选项 |
| | 复选框/单选框 | 勾选操作 |
| | 截图 | 截取当前页面 |
| **断言验证** | 验证标题 | 验证页面标题 |
| | 验证 URL | 验证当前 URL |
| | 验证文本 | 验证页面文本内容 |
| | 验证元素 | 验证元素存在/可见/可用 |
| **等待** | 等待时间 | 固定/随机等待 |
| | 等待元素 | 等待元素出现 |
| | 等待文本 | 等待文本出现 |
| **键盘操作** | 按键 | 模拟键盘按键 |
| | 组合键 | Ctrl+A、Ctrl+C 等 |
| **文件操作** | 上传文件 | 上传本地文件 |
| | 下载文件 | 下载远程文件 |
| **数据操作** | 获取/设置 Cookie | Cookie 操作 |
| | 获取/设置存储 | localStorage/sessionStorage |
| | 提取数据 | 从页面提取变量 |
| **高级** | 执行脚本 | 执行 JavaScript |
| | 处理弹窗 | 处理 alert/confirm |
| | 打开/关闭标签页 | 标签页操作 |

### 定位器格式

```yaml
# XPath
locator:
  type: xpath
  value: //input[@id='username']

# CSS Selector
locator:
  type: css
  value: .username-input

# ID
locator:
  type: id
  value: username

# Name
locator:
  type: name
  value: username

# Class
locator:
  type: class
  value: form-control

# Tag
locator:
  type: tag
  value: input

# 链接文本
locator:
  type: link_text
  value: 登录

# 部分链接文本
locator:
  type: partial_link_text
  value: 登
```

### 变量使用

在步骤参数中使用 `${变量名}` 格式引用变量：

```
URL: https://${base_url}/login
用户名: ${username}
密码: ${password}
```

变量优先级：**脚本变量 > 项目变量**

## 生产环境部署

### 1. 配置环境变量

```bash
# 后端
cd backend
cp .env.example .env
# 编辑 .env，修改 DJANGO_SECRET_KEY、域名等配置

# 前端
cd frontend
cp .env.example .env.production
# 编辑 .env.production，设置 VITE_API_BASE_URL
```

### 2. 后端部署

```bash
cd backend

# 使用生产配置迁移数据库
python manage.py migrate --settings=core.settings_prod

# 收集静态文件
python manage.py collectstatic --settings=core.settings_prod --noinput

# 使用 Gunicorn 启动
pip install gunicorn
gunicorn core.wsgi:application --settings core.settings_prod --bind 0.0.0.0:8000 --workers 4
```

### 3. 前端构建

```bash
cd frontend

# 构建生产版本
npm run build

# 生成的 dist 目录部署到 Nginx
```

### 4. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
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

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件
    location /static {
        alias /path/to/backend/staticfiles;
    }

    # 媒体文件
    location /media {
        alias /path/to/backend/media;
    }
}
```

### 部署检查清单

- [ ] 修改 `DJANGO_SECRET_KEY`
- [ ] 设置 `DJANGO_ALLOWED_HOSTS`
- [ ] 配置 `CORS_ALLOWED_ORIGINS`
- [ ] 配置 `CSRF_TRUSTED_ORIGINS`
- [ ] 设置 `DEBUG=False`
- [ ] 运行数据库迁移
- [ ] 收集静态文件
- [ ] 配置 Nginx 反向代理
- [ ] 配置 HTTPS (推荐)
- [ ] 创建远程执行机专用的RabbitMQ用户

> 详细部署说明请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 界面预览

### 项目管理
项目卡片式展示，支持 Web/移动端/API 三种类型

### 脚本编辑器
- 左侧：步骤类型面板（8大类，50+ 步骤类型）
- 中间：可视化画布 + JSON 编辑模式
- 右侧：步骤属性配置面板

### 执行管理
- 实时状态展示
- WebSocket 推送执行进度
- 支持手动停止执行

### 测试报告
- ECharts 图表展示
- 执行趋势、耗时分布、失败分析
- HTML 报告导出

### RabbitMQ用户管理（超级管理员专属）
- 紫色渐变卡片界面
- 创建/删除/修改密码
- 支持远程执行机连接

## 故障排查

### RabbitMQ 相关问题

#### 1. RabbitMQ 连接失败

**症状**: 后端日志显示 "Connection to RabbitMQ failed"

**解决方案**:
```bash
# Windows: 检查服务状态
Get-Service RabbitMQ

# Linux: 检查服务状态
sudo systemctl status rabbitmq-server

# 启动服务
rabbitmq-service start  # Windows
sudo systemctl start rabbitmq-server  # Linux
```

#### 2. 远程执行机无法连接RabbitMQ

**症状**: 远程执行机提示 "AMQPConnectionError" 或认证失败

**原因**: RabbitMQ 的 `guest` 账号默认只允许本地连接

**解决方案**:
1. 使用超级管理员账号登录平台
2. 进入「账号角色管理」→「角色管理」
3. 在「RabbitMQ 用户管理」区域创建专用用户
4. 将用户名和密码提供给执行机用户
5. 执行机配置向导中使用专用账号连接

#### 3. 队列未创建

**症状**: 执行机连接后，RabbitMQ管理界面看不到对应队列

**解决方案**:
- 检查执行机日志，确认 RabbitMQ 连接成功
- 查看执行机配置文件 `~/.executor/config.json`
- 确认 RabbitMQ 地址、端口、用户名密码配置正确

#### 4. 消息堆积

**症状**: 队列中消息数量持续增长

**解决方案**:
```bash
# 查看队列消息数
rabbitmqctl list_queues name messages

# 清空队列
rabbitmqctl purge_queue executor.xxx-xxx-xxx
```

### 执行器相关问题

#### 1. 执行机无法接收任务

**症状**: 执行机在线，但触发测试后没有反应

**检查步骤**:
1. 检查执行机是否成功连接到 RabbitMQ
2. 在 RabbitMQ 管理界面查看是否有对应队列
3. 检查执行机日志是否有消费任务的记录
4. 确认任务分发服务是否正常运行

#### 2. 执行机心跳未更新

**症状**: 平台显示执行机离线

**解决方案**:
- 检查执行机到平台的 HTTP 连接
- 查看 `/api/executor/heartbeat/` 端点是否可访问
- 确认执行机配置中的 `server_url` 正确

#### 3. 浏览器启动失败

**解决方案**:
- 检查浏览器是否已安装
- 查看日志文件了解详细错误
- 尝试手动指定浏览器路径

### WebSocket 相关问题

#### 1. 前端无法连接 WebSocket

**症状**: Web UI 无法显示实时状态

**解决方案**:
- 确认后端使用 `daphne` 启动，而非 `runserver`
- 检查防火墙设置
- 查看浏览器控制台错误信息

#### 2. WebSocket 连接断开

**解决方案**:
- 检查网络连接稳定性
- 前端实现了自动重连，稍等片刻会自动恢复
- 查看后端日志是否有异常

### 后端启动问题

#### 使用 runserver 而不是 daphne

**症状**: 日志显示 `Not Found: /ws/executor/`

**原因**: `python manage.py runserver` 不支持 WebSocket

**解决方案**:
```bash
# 错误的启动方式
python manage.py runserver

# 正确的启动方式
daphne -b 127.0.0.1 -p 8000 core.asgi:application
```

### 数据库问题

#### 迁移失败

**解决方案**:
```bash
# 重置数据库 (警告: 会清空所有数据)
rm backend/db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

### 调试技巧

#### 1. 查看日志

**后端日志**: 终端输出
**前端日志**: 浏览器开发者工具 Console
**执行机日志**: `~/.executor/logs/`
**RabbitMQ日志**: 根据安装路径查看

#### 2. 测试 RabbitMQ 连接

```python
# 测试脚本
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='127.0.0.1',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials('guest', 'guest')
    )
)
channel = connection.channel()
print("RabbitMQ 连接成功!")
connection.close()
```

#### 3. 测试 API 端点

```bash
# 测试心跳API
curl -X POST http://localhost:8000/api/executor/heartbeat/ \
  -H "Content-Type: application/json" \
  -d '{"executor_uuid": "test", "cpu_usage": 0, "memory_usage": 0}'
```

### 常见错误代码

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `AMQPConnectionError` | RabbitMQ 未启动 | 启动 RabbitMQ 服务 |
| `AuthenticationError` | RabbitMQ 认证失败 | 检查用户名密码，远程连接需使用专用账号 |
| `NotFound: /ws/` | WebSocket 路由未找到 | 使用 daphne 启动 |
| `401 Unauthorized` | API 认证失败 | 检查登录状态 |
| `403 Forbidden` | 权限不足 | 检查用户角色权限 |
| `500 Internal Error` | 服务器错误 | 查看后端日志 |

## 更多文档

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | **系统架构文档** - 任务分发机制、执行模式详解 |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | 详细的生产环境部署指南 |
| [MQ_SUMMARY.md](./MQ_SUMMARY.md) | 消息队列架构迁移总结 |
| [RABBITMQ_INSTALL.md](./RABBITMQ_INSTALL.md) | RabbitMQ 安装指南 |
| [RABBITMQ_STATUS.md](./RABBITMQ_STATUS.md) | RabbitMQ 状态检查 |
| [executor-client/README.md](./executor-client/README.md) | 执行器客户端详细文档 |
| [executor-client/使用说明.md](./executor-client/使用说明.md) | 执行器客户端使用说明 |

## 系统要求

### 开发环境

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| Python | 3.9 | 3.11+ |
| Node.js | 16 | 18 LTS |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 2GB | 10GB+ |

### 生产环境

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 16GB+ |
| 数据库 | SQLite | PostgreSQL 13+ |
| 消息队列 | RabbitMQ 3.12+ | RabbitMQ 集群 |

## 浏览器支持

| 浏览器 | 版本 |
|--------|------|
| Chrome | 90+ |
| Firefox | 88+ |
| Edge | 90+ |
| Safari | 14+ |

## 路线图

### v1.2 (计划中)
- [ ] 支持更多测试框架 (Cypress, Robot Framework)
- [ ] CI/CD 集成 (Jenkins, GitLab CI)
- [ ] 测试数据自动生成
- [ ] 性能测试支持

### v2.0 (未来)
- [ ] 分布式执行集群
- [ ] AI 辅助测试用例生成
- [ ] 移动端 APP 支持
- [ ] 云原生部署 (Kubernetes)

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License

## 联系方式

- 问题反馈: 请提交 GitHub Issue
- 技术讨论: 欢迎 Pull Request

---

**最后更新**: 2026-02-11
