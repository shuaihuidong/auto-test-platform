"""
启动 ASGI 服务器（支持 WebSocket）
使用 daphne 而不是 runserver
"""

import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # 使用 daphne 启动 ASGI 服务器
    import daphne.server
    from django.core.asgi import get_asgi_application

    # 获取 ASGI 应用
    application = get_asgi_application()

    # 启动 daphne 服务器
    from daphne.testing import DaphneServer
    import twisted

    print("=" * 50)
    print("启动自动化测试平台服务器 (ASGI + WebSocket)")
    print("=" * 50)
    print("WebSocket: ws://127.0.0.1:8000/ws/executor/")
    print("API: http://127.0.0.1:8000/api/")
    print("=" * 50)

    # 使用命令行方式启动 daphne
    import subprocess
    subprocess.run([
        sys.executable, '-m', 'daphne',
        '-b', '0.0.0.0',
        '-p', '8000',
        'core.asgi:application'
    ])
