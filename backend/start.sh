#!/bin/bash
set -e

echo "Starting Django backend..."

# 运行数据库迁移
echo "Running migrations..."
python manage.py migrate --noinput

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 启动 Daphne 服务器
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8000 core.asgi:application
