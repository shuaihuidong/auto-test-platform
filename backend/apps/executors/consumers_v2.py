"""
WebSocket Consumers - 简化版

仅用于 Web UI 实时状态展示：
- 执行机上线/离线事件
- 执行机状态变化通知
- 任务状态更新通知

任务下发已迁移到消息队列 (RabbitMQ)
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ExecutorStatusConsumer(AsyncWebsocketConsumer):
    """
    执行机状态 WebSocket Consumer

    用于 Web UI 实时监听执行机状态变化
    """

    async def connect(self):
        """建立连接"""
        # 获取执行机 ID（可选，用于监听特定执行机）
        from urllib.parse import parse_qs

        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        executor_id = params.get('executor_id', [None])[0]

        self.executor_id = executor_id
        self.group_name = 'executor_status'

        # 加入状态广播组
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        logger.info(f"客户端已连接到执行机状态监听: executor_id={executor_id}")

    async def disconnect(self, close_code):
        """断开连接"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """接收消息（客户端可以发送控制命令）"""
        try:
            message = json.loads(text_data)
            msg_type = message.get('type')

            if msg_type == 'subscribe_executor':
                # 订阅特定执行机的状态
                executor_id = message.get('executor_id')
                if executor_id:
                    self.executor_id = executor_id
                    logger.info(f"客户端订阅执行机: {executor_id}")

        except Exception as e:
            logger.error(f"处理消息失败: {e}")

    # 事件处理器（通过 channel_layer 调用）

    async def executor_online(self, event):
        """执行机上线事件"""
        await self.send(text_data=json.dumps({
            'type': 'executor_online',
            'data': event.get('data', {})
        }))

    async def executor_offline(self, event):
        """执行机离线事件"""
        await self.send(text_data=json.dumps({
            'type': 'executor_offline',
            'data': event.get('data', {})
        }))

    async def executor_status_update(self, event):
        """执行机状态更新事件"""
        # 如果订阅了特定执行机，只发送该执行机的更新
        executor_id = event.get('data', {}).get('executor_id')
        if self.executor_id and executor_id != self.executor_id:
            return

        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'data': event.get('data', {})
        }))

    async def task_started(self, event):
        """任务开始事件"""
        await self.send(text_data=json.dumps({
            'type': 'task_started',
            'data': event.get('data', {})
        }))

    async def task_completed(self, event):
        """任务完成事件"""
        await self.send(text_data=json.dumps({
            'type': 'task_completed',
            'data': event.get('data', {})
        }))

    async def task_failed(self, event):
        """任务失败事件"""
        await self.send(text_data=json.dumps({
            'type': 'task_failed',
            'data': event.get('data', {})
        }))


# 辅助函数：广播执行机状态变化
async def broadcast_executor_status(executor_id: int, status: str, **kwargs):
    """
    广播执行机状态变化

    Args:
        executor_id: 执行机 ID
        status: 状态 (online/offline/idle/busy)
        **kwargs: 额外数据
    """
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    data = {
        'executor_id': executor_id,
        'status': status,
        'timestamp': timezone.now().isoformat(),
        **kwargs
    }

    if status == 'online':
        event_type = 'executor.online'
    elif status == 'offline':
        event_type = 'executor.offline'
    else:
        event_type = 'executor.status_update'

    await channel_layer.group_send(
        'executor_status',
        {
            'type': event_type,
            'data': data
        }
    )


# 辅助函数：广播任务状态变化
async def broadcast_task_status(task_id: int, status: str, **kwargs):
    """
    广播任务状态变化

    Args:
        task_id: 任务 ID
        status: 状态 (started/completed/failed)
        **kwargs: 额外数据
    """
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    data = {
        'task_id': task_id,
        'status': status,
        'timestamp': timezone.now().isoformat(),
        **kwargs
    }

    if status == 'running':
        event_type = 'task.started'
    elif status == 'completed':
        event_type = 'task.completed'
    elif status == 'failed':
        event_type = 'task.failed'
    else:
        return

    await channel_layer.group_send(
        'executor_status',
        {
            'type': event_type,
            'data': data
        }
    )
