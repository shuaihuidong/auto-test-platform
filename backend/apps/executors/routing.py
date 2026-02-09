from django.urls import re_path
from . import consumers_v2

websocket_urlpatterns = [
    # 用于执行器状态展示
    re_path(r'ws/executor-status/?$', consumers_v2.ExecutorStatusConsumer.as_asgi()),
]
