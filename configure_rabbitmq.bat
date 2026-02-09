@echo off
REM RabbitMQ 配置脚本 - 请以管理员身份运行

echo ========================================
echo RabbitMQ 环境变量配置
echo ========================================
echo.

REM 设置 ERLANG_HOME
setx ERLANG_HOME "C:\Program Files\Erlang OTP" /M
if %errorlevel% equ 0 (
    echo [OK] ERLANG_HOME 已设置
) else (
    echo [ERROR] 需要管理员权限
    pause
    exit /b 1
)

echo.
echo ========================================
echo 启用 RabbitMQ 管理插件
echo ========================================
echo.

cd /d "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.12.10\sbin"
rabbitmq-plugins.bat enable rabbitmq_management

echo.
echo ========================================
echo 启动 RabbitMQ 服务
echo ========================================
echo.

rabbitmq-service.bat start

echo.
echo ========================================
echo 验证安装
echo ========================================
echo.

rabbitmqctl.bat status

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 管理界面: http://localhost:15672
echo 用户名: guest
echo 密码: guest
echo.
echo 按任意键打开管理界面...
pause >nul

start http://localhost:15672
