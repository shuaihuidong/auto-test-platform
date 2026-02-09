"""
Message Queue Service - 任务消息队列服务

使用 RabbitMQ 实现任务分发：
- Exchange: tasks.exchange (topic, durable)
- Queue: executor.{uuid} (durable, exclusive)
- Routing Key: executor.{uuid}
"""

import json
import logging
from typing import Optional, Dict, Any
from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
    BasicProperties,
    exceptions
)
from django.conf import settings

logger = logging.getLogger(__name__)


class MessageQueueError(Exception):
    """消息队列错误"""
    pass


class MessageQueuePublisher:
    """
    消息队列发布者

    负责将任务发布到 RabbitMQ exchange
    """

    # Exchange 配置
    EXCHANGE_NAME = 'tasks.exchange'
    EXCHANGE_TYPE = 'topic'

    def __init__(self):
        self._connection: Optional[BlockingConnection] = None
        self._channel = None
        self._config = self._get_config()

    def _get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return {
            'host': getattr(settings, 'RABBITMQ_HOST', '127.0.0.1'),
            'port': getattr(settings, 'RABBITMQ_PORT', 5672),
            'username': getattr(settings, 'RABBITMQ_USER', 'guest'),
            'password': getattr(settings, 'RABBITMQ_PASSWORD', 'guest'),
            'vhost': getattr(settings, 'RABBITMQ_VHOST', '/'),
        }

    def connect(self) -> bool:
        """
        建立连接

        Returns:
            是否连接成功
        """
        try:
            credentials = PlainCredentials(
                self._config['username'],
                self._config['password']
            )
            parameters = ConnectionParameters(
                host=self._config['host'],
                port=self._config['port'],
                virtual_host=self._config['vhost'],
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )

            self._connection = BlockingConnection(parameters)
            self._channel = self._connection.channel()

            # 声明 exchange (durable=True 持久化)
            self._channel.exchange_declare(
                exchange=self.EXCHANGE_NAME,
                exchange_type=self.EXCHANGE_TYPE,
                durable=True
            )
            logger.info(f"Exchange '{self.EXCHANGE_NAME}' 已声明")

            return True

        except Exception as e:
            logger.error(f"连接 RabbitMQ 失败: {e}")
            return False

    def publish_task(self, executor_uuid: str, task_data: Dict[str, Any]) -> bool:
        """
        发布任务到指定执行机的队列

        Args:
            executor_uuid: 执行机 UUID
            task_data: 任务数据

        Returns:
            是否发布成功
        """
        try:
            # 如果没有连接，先连接
            if not self._connection or self._connection.is_closed:
                if not self.connect():
                    return False

            # 序列化任务数据
            message_body = json.dumps(task_data, ensure_ascii=False)

            # 发布消息
            routing_key = f'executor.{executor_uuid}'
            self._channel.basic_publish(
                exchange=self.EXCHANGE_NAME,
                routing_key=routing_key,
                body=message_body,
                properties=BasicProperties(
                    delivery_mode=2,  # 持久化消息
                    content_type='application/json'
                )
            )

            logger.info(f"任务已发布: routing_key={routing_key}, task_id={task_data.get('task_id')}")
            return True

        except Exception as e:
            logger.error(f"发布任务失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            logger.info("RabbitMQ 连接已关闭")


# 同步版本的发布者（用于 Django 视图调用）
class SyncMessageQueuePublisher:
    """
    同步消息队列发布者

    使用 BlockingConnection 适合在 Django 请求处理中调用
    """

    EXCHANGE_NAME = 'tasks.exchange'
    EXCHANGE_TYPE = 'topic'

    def __init__(self):
        import pika
        self.pika = pika  # 保存引用供后续使用
        self._connection = None
        self._channel = None
        self._config = self._get_config()

    def _get_config(self) -> Dict[str, Any]:
        """获取配置"""
        from django.conf import settings
        return {
            'host': getattr(settings, 'RABBITMQ_HOST', '127.0.0.1'),
            'port': getattr(settings, 'RABBITMQ_PORT', 5672),
            'username': getattr(settings, 'RABBITMQ_USER', 'guest'),
            'password': getattr(settings, 'RABBITMQ_PASSWORD', 'guest'),
            'vhost': getattr(settings, 'RABBITMQ_VHOST', '/'),
        }

    def _connect(self) -> bool:
        """建立连接"""
        try:
            credentials = self.pika.PlainCredentials(
                self._config['username'],
                self._config['password']
            )
            parameters = self.pika.ConnectionParameters(
                host=self._config['host'],
                port=self._config['port'],
                virtual_host=self._config['vhost'],
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )

            self._connection = self.pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

            # 声明 exchange
            self._channel.exchange_declare(
                exchange=self.EXCHANGE_NAME,
                exchange_type=self.EXCHANGE_TYPE,
                durable=True
            )

            return True

        except Exception as e:
            logger.error(f"连接 RabbitMQ 失败: {e}")
            return False

    def publish_task(self, executor_uuid: str, task_data: Dict[str, Any]) -> bool:
        """
        发布任务到指定执行机的队列

        Args:
            executor_uuid: 执行机 UUID
            task_data: 任务数据

        Returns:
            是否发布成功
        """
        try:
            # 确保已连接
            if not self._channel or self._connection.is_closed:
                if not self._connect():
                    return False

            # 序列化任务数据
            message_body = json.dumps(task_data, ensure_ascii=False)

            # 发布消息
            routing_key = f'executor.{executor_uuid}'
            self._channel.basic_publish(
                exchange=self.EXCHANGE_NAME,
                routing_key=routing_key,
                body=message_body,
                properties=self.pika.BasicProperties(
                    delivery_mode=2,  # 持久化消息
                    content_type='application/json'
                )
            )

            logger.info(f"任务已发布: routing_key={routing_key}, task_id={task_data.get('task_id')}")
            return True

        except Exception as e:
            logger.error(f"发布任务失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        if self._connection and not self._connection.is_closed:
            self._connection.close()


# 全局单例
_publisher: Optional[SyncMessageQueuePublisher] = None


def get_message_queue_publisher() -> SyncMessageQueuePublisher:
    """获取消息队列发布者单例"""
    global _publisher
    if _publisher is None:
        _publisher = SyncMessageQueuePublisher()
    return _publisher
