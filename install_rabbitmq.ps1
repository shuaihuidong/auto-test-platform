# RabbitMQ 自动安装脚本
# 请以管理员身份运行此脚本

Write-Host "=== RabbitMQ 自动安装 ===" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "请以管理员身份运行此脚本" -ForegroundColor Red
    Write-Host "右键点击 PowerShell，选择 '以管理员身份运行'" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit
}

# 创建临时目录
$tempDir = Join-Path $env:TEMP "RabbitMQInstall"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

Write-Host "下载目录: $tempDir" -ForegroundColor Gray
Write-Host ""

# 下载链接
$erlangUrl = "https://github.com/erlang/otp/releases/download/OTP-26.2.1/otp_win64_26.2.1.exe"
$rabbitmqUrl = "https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.12.10/rabbitmq-server-3.12.10.exe"

$erlangFile = Join-Path $tempDir "otp_win64_26.2.1.exe"
$rabbitmqFile = Join-Path $tempDir "rabbitmq-server-3.12.10.exe"

# 下载 Erlang
Write-Host "[1/4] 下载 Erlang/OTP..." -ForegroundColor Yellow
try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $erlangUrl -OutFile $erlangFile -UseBasicParsing
    Write-Host "✓ Erlang 下载完成" -ForegroundColor Green
} catch {
    Write-Host "✗ Erlang 下载失败: $_" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit
}

# 下载 RabbitMQ
Write-Host "[2/4] 下载 RabbitMQ Server..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $rabbitmqUrl -OutFile $rabbitmqFile -UseBasicParsing
    Write-Host "✓ RabbitMQ 下载完成" -ForegroundColor Green
} catch {
    Write-Host "✗ RabbitMQ 下载失败: $_" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit
}

# 安装 Erlang
Write-Host "[3/4] 安装 Erlang/OTP..." -ForegroundColor Yellow
Write-Host "请在新窗口中完成 Erlang 安装（使用默认设置）" -ForegroundColor Cyan
Start-Process -FilePath $erlangFile -Wait
Write-Host "✓ Erlang 安装完成" -ForegroundColor Green

# 安装 RabbitMQ
Write-Host "[4/4] 安装 RabbitMQ Server..." -ForegroundColor Yellow
Write-Host "请在新窗口中完成 RabbitMQ 安装（使用默认设置）" -ForegroundColor Cyan
Start-Process -FilePath $rabbitmqFile -Wait
Write-Host "✓ RabbitMQ 安装完成" -ForegroundColor Green

Write-Host ""
Write-Host "=== 配置 RabbitMQ ===" -ForegroundColor Cyan

# 查找 RabbitMQ 安装目录
$rabbitmqDirs = @(
    "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.12\sbin",
    "C:\Program Files (x86)\RabbitMQ Server\rabbitmq_server-3.12\sbin"
)

$sbinDir = $null
foreach ($dir in $rabbitmqDirs) {
    if (Test-Path $dir) {
        $sbinDir = $dir
        break
    }
}

if ($null -eq $sbinDir) {
    Write-Host "✗ 找不到 RabbitMQ 安装目录" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit
}

Write-Host "RabbitMQ 目录: $sbinDir" -ForegroundColor Gray
Write-Host ""

# 启用管理插件
Write-Host "[1/3] 启用管理插件..." -ForegroundColor Yellow
$pluginsScript = Join-Path $sbinDir "rabbitmq-plugins.bat"
& $pluginsScript enable rabbitmq_management
Write-Host "✓ 管理插件已启用" -ForegroundColor Green

# 启动服务
Write-Host "[2/3] 启动 RabbitMQ 服务..." -ForegroundColor Yellow
$serviceScript = Join-Path $sbinDir "rabbitmq-service.bat"
try {
    & $serviceScript start
    Write-Host "✓ RabbitMQ 服务已启动" -ForegroundColor Green
} catch {
    Write-Host "× 启动服务失败，请手动启动" -ForegroundColor Yellow
}

# 验证状态
Write-Host "[3/3] 验证安装..." -ForegroundColor Yellow
$ctlScript = Join-Path $sbinDir "rabbitmqctl.bat"
& $ctlScript status

Write-Host ""
Write-Host "=== 安装完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "管理界面: http://localhost:15672" -ForegroundColor Cyan
Write-Host "用户名: guest" -ForegroundColor Cyan
Write-Host "密码: guest" -ForegroundColor Cyan
Write-Host ""
Write-Host "按回车键打开管理界面..."
Read-Host

Start-Process "http://localhost:15672"

# 清理临时文件
Write-Host "清理临时文件..."
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
