# 自动化测试平台 - 执行机客户端

## 概述

执行机是自动化测试平台的任务执行组件，负责接收并执行从平台下发的测试任务。执行机通过 RabbitMQ 消息队列接收任务，通过 HTTP API 上报执行结果和心跳状态。

## 系统要求

### 必需环境
- **Python**: 3.8 或更高版本
- **RabbitMQ**: 3.8 或更高版本（用于消息队列）
- **浏览器**: Chrome/Firefox/Edge（根据需要安装）

### 浏览器驱动
根据使用的浏览器，需要安装对应的驱动：

| 浏览器 | 驱动 | 下载地址 |
|--------|------|----------|
| Chrome | ChromeDriver | https://chromedriver.chromium.org/ |
| Firefox | GeckoDriver | https://github.com/mozilla/geckodriver |
| Edge | MSEdgeDriver | 通常随 Edge 浏览器自动安装 |

## 安装

### 方式一：安装包安装（推荐）

1. 双击运行 `executor-setup-x.x.x.exe`
2. 按照安装向导完成安装
3. 首次运行会自动启动配置向导
4. 配置服务器地址和账号信息

### 方式二：手动安装

1. 解压执行机文件到目标目录
2. 安装依赖：`pip install -r requirements.txt`
3. 运行：`python main.py`

## 配置

执行机配置文件位于：`~/.executor/config.json`

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| server_url | 平台服务器地址 | http://127.0.0.1:8000 |
| executor_name | 执行机名称 | - |
| owner_username | 平台用户名 | - |
| owner_password | 平台密码 | - |
| max_concurrent | 最大并发任务数 | 3 |
| default_browser | 默认浏览器 | chrome |
| rabbitmq_host | RabbitMQ 地址 | 127.0.0.1 |
| rabbitmq_port | RabbitMQ 端口 | 5672 |
| heartbeat_interval | 心跳间隔（秒） | 30 |

## 使用

### 启动执行机

双击桌面快捷方式或开始菜单中的"自动化测试执行机"。

### 连接服务器

1. 确保平台服务已启动
2. 确保 RabbitMQ 服务已启动
3. 点击"连接服务器"按钮
4. 连接成功后状态显示为"已连接"

### 查看任务状态

- **当前任务**：显示正在执行和最近完成的任务
- **统计信息**：显示总任务数、成功数、失败数、资源使用情况

### 开机自启动

在安装向导中可以选择是否开机自启动。如需修改：

1. 打开任务计划程序（Windows）
2. 找到"自动化测试执行机"任务
3. 启用或禁用该任务

## 日志

### 日志位置

- 控制台日志：执行机窗口
- 文件日志：`~/.executor/logs/`

### 日志级别

- WARNING：警告信息（默认）
- ERROR：错误信息
- INFO：详细信息
- DEBUG：调试信息

修改日志级别：编辑配置文件中的 `log_level` 字段。

## 故障排查

### 问题：无法连接服务器

**原因**：
- 平台服务未启动
- RabbitMQ 服务未启动
- 网络配置问题
- 防火墙阻止连接

**解决方案**：
1. 检查平台服务是否运行：访问 http://服务器地址:8000
2. 检查 RabbitMQ 是否运行：访问 http://localhost:15672（默认管理界面）
3. 检查配置文件中的服务器地址是否正确
4. 检查防火墙设置

### 问题：无法启动浏览器

**原因**：
- 浏览器未安装
- 浏览器驱动版本不匹配
- 浏览器路径配置错误

**解决方案**：
1. 确认浏览器已安装
2. 下载与浏览器版本匹配的驱动
3. 在配置向导中设置正确的浏览器和驱动路径

### 问题：任务执行失败

**原因**：
- 脚本配置错误
- 元素定位失败
- 网络超时
- 测试页面问题

**解决方案**：
1. 查看日志获取详细错误信息
2. 在平台查看脚本详情
3. 使用浏览器开发者工具检查元素定位

## 技术支持

- 项目地址：https://github.com/your-org/auto-test-platform
- 问题反馈：https://github.com/your-org/auto-test-platform/issues

## 版本历史

### v1.0.0 (2024-02-08)
- 初始版本
- 支持 Selenium WebDriver
- 支持 RabbitMQ 消息队列
- 支持 HTTP 心跳上报
- 支持多浏览器执行
