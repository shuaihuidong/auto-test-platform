# RabbitMQ 快速安装脚本 (Windows)
# 使用 Chocolatey 安装 RabbitMQ

Write-Host "=== RabbitMQ 快速安装脚本 ===" -ForegroundColor Cyan

# 检查是否已安装 Chocolatey
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Chocolatey 未安装，正在安装..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# 安装 RabbitMQ
Write-Host "正在安装 RabbitMQ..." -ForegroundColor Yellow
choco install rabbitmq -y

# 启用管理插件
Write-Host "启用管理插件..." -ForegroundColor Yellow
& "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.12\sbin\rabbitmq-plugins.bat" enable rabbitmq_management

# 启动 RabbitMQ 服务
Write-Host "启动 RabbitMQ 服务..." -ForegroundColor Yellow
& "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.12\sbin\rabbitmq-service.bat" start

Write-Host ""
Write-Host "=== 安装完成 ===" -ForegroundColor Green
Write-Host "管理界面: http://localhost:15672" -ForegroundColor Cyan
Write-Host "默认用户名: guest" -ForegroundColor Cyan
Write-Host "默认密码: guest" -ForegroundColor Cyan
Write-Host ""
Write-Host "AMQP 端口: 5672" -ForegroundColor Cyan
Write-Host "管理端口: 15672" -ForegroundColor Cyan
