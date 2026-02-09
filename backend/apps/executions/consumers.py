"""
WebSocket消费者 - 实时推送执行状态
"""
import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Execution


class ExecutionConsumer(AsyncJsonWebsocketConsumer):
    """
    执行实时状态推送消费者
    """

    async def connect(self):
        """建立WebSocket连接"""
        self.execution_id = self.scope['url_route']['kwargs']['execution_id']
        self.group_name = f'execution_{self.execution_id}'

        # 加入组
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        """
        接收客户端消息

        支持的操作:
        - pause: 暂停执行
        - resume: 恢复执行
        - stop: 停止执行
        - step: 单步执行
        - set_breakpoint: 设置断点
        - remove_breakpoint: 移除断点
        - get_variables: 获取变量
        """
        action = content.get('action')

        if action == 'pause':
            await self.handle_pause()

        elif action == 'resume':
            await self.handle_resume()

        elif action == 'stop':
            await self.handle_stop()

        elif action == 'step':
            await self.handle_step()

        elif action == 'set_breakpoint':
            step_index = content.get('step_index')
            await self.handle_set_breakpoint(step_index)

        elif action == 'remove_breakpoint':
            step_index = content.get('step_index')
            await self.handle_remove_breakpoint(step_index)

        elif action == 'get_variables':
            await self.handle_get_variables()

    async def handle_pause(self):
        """处理暂停请求"""
        # 向执行器发送暂停信号
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'execution_message',
                'action': 'pause',
                'data': {'status': 'pausing'}
            }
        )

    async def handle_resume(self):
        """处理恢复请求"""
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'execution_message',
                'action': 'resume',
                'data': {'status': 'resuming'}
            }
        )

    async def handle_stop(self):
        """处理停止请求"""
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'execution_message',
                'action': 'stop',
                'data': {'status': 'stopping'}
            }
        )

    async def handle_step(self):
        """处理单步执行请求"""
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'execution_message',
                'action': 'step',
                'data': {'status': 'stepping'}
            }
        )

    async def handle_set_breakpoint(self, step_index: int):
        """处理设置断点请求"""
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'execution_message',
                'action': 'set_breakpoint',
                'data': {'step_index': step_index}
            }
        )

    async def handle_remove_breakpoint(self, step_index: int):
        """处理移除断点请求"""
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'execution_message',
                'action': 'remove_breakpoint',
                'data': {'step_index': step_index}
            }
        )

    async def handle_get_variables(self):
        """处理获取变量请求"""
        variables = await self.get_execution_variables()
        await self.send_json({
            'type': 'variables',
            'data': variables
        })

    @database_sync_to_async
    def get_execution_variables(self):
        """从数据库获取执行变量"""
        try:
            execution = Execution.objects.get(id=self.execution_id)
            return execution.variables_snapshot
        except Execution.DoesNotExist:
            return {}

    async def execution_message(self, event):
        """
        处理执行消息

        这个方法被channel_layer调用，用于向客户端推送执行状态更新
        """
        message = event.get('data', {})
        await self.send_json(message)


class ExecutionLogConsumer(AsyncJsonWebsocketConsumer):
    """
    执行日志推送消费者
    """

    async def connect(self):
        """建立WebSocket连接"""
        self.execution_id = self.scope['url_route']['kwargs']['execution_id']
        self.group_name = f'execution_log_{self.execution_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def log_message(self, event):
        """推送日志消息"""
        log_data = event.get('data', {})
        await self.send_json({
            'type': 'log',
            'data': log_data
        })
