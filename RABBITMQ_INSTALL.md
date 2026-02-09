# RabbitMQ 安装指南

## 下载链接

### 方式一：直接下载安装（推荐）

1. **Erlang/OTP** (RabbitMQ 依赖)
   - 官方下载: https://erlang.org/download.html
   - 直接下载: https://github.com/erlang/otp/releases/download/OTP-26.2.1/otp_win64_26.2.1.exe
   - 安装到默认路径: `C:\Program Files\Erlang OTP`

2. **RabbitMQ Server**
   - 官方下载: https://www.rabbitmq.com/download.html
   - 直接下载: https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.12.10/rabbitmq-server-3.12.10.exe
   - 安装到默认路径: `C:\Program Files\RabbitMQ Server`

### 安装步骤

1. 先安装 Erlang/OTP
2. 再安装 RabbitMQ Server
3. 重启电脑（推荐）

### 安装后配置

打开 PowerShell（管理员身份）：

```powershell
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.12\sbin"

# 1. 启用管理插件
.\rabbitmq-plugins.bat enable rabbitmq_management

# 2. 启动服务
.\rabbitmq-service.bat start

# 3. 验证状态
.\rabbitmqctl.bat status
```

### 访问管理界面

- URL: http://localhost:15672
- 用户名: `guest`
- 密码: `guest`

### 配置执行机

安装 RabbitMQ 后，执行机配置文件会自动使用默认设置：

```json
{
  "rabbitmq_host": "127.0.0.1",
  "rabbitmq_port": 5672,
  "rabbitmq_user": "guest",
  "rabbitmq_password": "guest",
  "rabbitmq_vhost": "/"
}
```

### 快速测试

```powershell
# 查看队列列表
.\rabbitmqctl.bat list_queues

# 查看连接列表
.\rabbitmqctl.bat list_connections
```
