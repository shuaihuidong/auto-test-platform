@echo off
echo ====================================
echo  自动化测试平台 - 后端服务器
echo ====================================
echo.
echo API: http://127.0.0.1:8000/api/
echo WebSocket: ws://127.0.0.1:8000/ws/executor/
echo.
echo 正在启动 Daphne ASGI 服务器...
echo (按 Ctrl+C 停止服务器)
echo.

python -m daphne -b 0.0.0.0 -p 8000 core.asgi:application

pause
