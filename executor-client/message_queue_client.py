"""
Message Queue Consumer - 任务消息队列消费者

执行机客户端用于从 RabbitMQ 接收任务：
- 连接 RabbitMQ
- 声明专属队列 executor.{uuid}
- 绑定到 tasks.exchange，routing key 为 executor.{uuid}
- 消费任务并 ACK/NACK
"""

import json
import logging
import time
import threading
from typing import Callable, Optional, Dict, Any
from pika import (
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
    spec
)
from pika.exceptions import (
    ConnectionClosed,
    ChannelClosed,
    AMQPConnectionError,
    AMQPChannelError
)
from loguru import logger

from config import get_config_manager, ExecutorConfig


class MessageQueueConsumer:
    """
    消息队列消费者

    负责从 RabbitMQ 接收任务并执行
    """

    EXCHANGE_NAME = 'tasks.exchange'
    EXCHANGE_TYPE = 'topic'

    def __init__(self):
        self.config: ExecutorConfig = get_config_manager().get()
        self._connection: Optional[BlockingConnection] = None
        self._channel = None
        self._is_running = False
        self._consumer_thread: Optional[threading.Thread] = None

        # 回调函数
        self.on_task_received: Optional[Callable] = None  # 收到任务时回调
        self.on_connected: Optional[Callable] = None      # 连接成功时回调
        self.on_disconnected: Optional[Callable] = None   # 断开连接时回调
        self.on_error: Optional[Callable] = None          # 发生错误时回调

        # RabbitMQ 配置
        self._mq_config = self._get_mq_config()

    def _get_mq_config(self) -> Dict[str, Any]:
        """获取 RabbitMQ 配置"""
        return {
            'host': getattr(self.config, 'rabbitmq_host', '127.0.0.1'),
            'port': getattr(self.config, 'rabbitmq_port', 5672),
            'username': getattr(self.config, 'rabbitmq_user', 'guest'),
            'password': getattr(self.config, 'rabbitmq_password', 'guest'),
            'vhost': getattr(self.config, 'rabbitmq_vhost', '/'),
        }

    def _connect(self) -> bool:
        """
        建立连接

        Returns:
            是否连接成功
        """
        try:
            credentials = PlainCredentials(
                self._mq_config['username'],
                self._mq_config['password']
            )
            parameters = ConnectionParameters(
                host=self._mq_config['host'],
                port=self._mq_config['port'],
                virtual_host=self._mq_config['vhost'],
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
                connection_attempts=5,
                retry_delay=5
            )

            self._connection = BlockingConnection(parameters)
            self._channel = self._connection.channel()

            # 设置 QoS，每次只预取一条消息
            self._channel.basic_qos(prefetch_count=1)

            logger.info("RabbitMQ 连接已建立")
            return True

        except Exception as e:
            logger.error(f"连接 RabbitMQ 失败: {e}")
            return False

    def _setup_queue(self) -> bool:
        """
        设置队列和绑定

        Returns:
            是否设置成功
        """
        try:
            # 声明 exchange
            self._channel.exchange_declare(
                exchange=self.EXCHANGE_NAME,
                exchange_type=self.EXCHANGE_TYPE,
                durable=True
            )

            # 声明专属队列（持久化）
            queue_name = f'executor.{self.config.executor_uuid}'
            self._channel.queue_declare(
                queue=queue_name,
                durable=True,
                exclusive=False,  # 不独享，允许多个连接
                auto_delete=False  # 不自动删除
            )

            # 绑定队列到 exchange
            routing_key = f'executor.{self.config.executor_uuid}'
            self._channel.queue_bind(
                queue=queue_name,
                exchange=self.EXCHANGE_NAME,
                routing_key=routing_key
            )

            logger.info(f"队列已设置: {queue_name} -> {routing_key}")
            return True

        except Exception as e:
            logger.error(f"设置队列失败: {e}")
            return False

    def _on_message_received(self, channel, method, properties, body):
        """
        收到消息的回调

        Args:
            channel: RabbitMQ channel
            method: delivery method
            properties: message properties
            body: message body (JSON bytes)
        """
        try:
            # 解析消息
            message = json.loads(body.decode('utf-8'))
            task_id = message.get('task_id', '')
            print(f"[DEBUG] MQ received task: {task_id}")
            logger.info(f"收到任务: {task_id}")

            # 调用任务处理回调
            if self.on_task_received:
                try:
                    # 在新线程中执行任务，避免阻塞消费者
                    result = self.on_task_received(message)

                    if result:
                        # 任务成功，ACK
                        channel.basic_ack(delivery_tag=method.delivery_tag)
                        logger.info(f"任务 {task_id} 完成，已 ACK")
                    else:
                        # 任务被拒绝，NACK 并重新入队
                        # 注意：执行机端已移除并发限制检查，正常情况下不会走到这里
                        channel.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=True  # 重新入队，避免任务丢失
                        )
                        logger.warning(f"任务 {task_id} 被拒绝，已 NACK 重新入队")

                except Exception as e:
                    logger.error(f"处理任务时出错: {e}", exc_info=True)
                    # 发生异常，NACK 并重新入队
                    channel.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=True
                    )
            else:
                # 没有回调函数，直接 ACK
                channel.basic_ack(delivery_tag=method.delivery_tag)
                logger.warning("没有设置任务处理回调，消息已 ACK")

        except json.JSONDecodeError as e:
            logger.error(f"消息解析失败: {e}")
            # 消息格式错误，直接 ACK（不重新入队避免死循环）
            channel.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"处理消息时发生未知错误: {e}", exc_info=True)
            # 未知错误，NACK 重新入队
            try:
                channel.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=True
                )
            except:
                pass

    def start(self) -> bool:
        """
        启动消费者

        Returns:
            是否启动成功
        """
        if self._is_running:
            logger.warning("消费者已在运行中")
            return True

        try:
            # 连接 RabbitMQ
            if not self._connect():
                return False

            # 设置队列
            if not self._setup_queue():
                return False

            # 开始消费
            queue_name = f'executor.{self.config.executor_uuid}'
            self._channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._on_message_received,
                auto_ack=False
            )

            self._is_running = True

            # 触发连接成功回调
            if self.on_connected:
                try:
                    self.on_connected()
                except Exception as e:
                    logger.error(f"连接成功回调出错: {e}")

            logger.info("消费者已启动，开始接收任务...")

            # 在新线程中启动消费循环
            self._consumer_thread = threading.Thread(
                target=self._consume_loop,
                daemon=True,
                name="MQConsumer"
            )
            self._consumer_thread.start()

            return True

        except Exception as e:
            logger.error(f"启动消费者失败: {e}")
            return False

    def _consume_loop(self):
        """消费循环（在单独线程中运行）"""
        while self._is_running and self._connection and not self._connection.is_closed:
            try:
                # 使用 process_data_events 而不是 start_consuming
                # 这样可以定期检查 _is_running 标志
                self._connection.process_data_events(time_limit=1)

            except (ConnectionClosed, AMQPConnectionError) as e:
                logger.warning(f"连接已关闭: {e}")
                if self._is_running:
                    # 尝试重连
                    logger.info("尝试重新连接...")
                    time.sleep(5)
                    if self._connect():
                        self._setup_queue()
                        queue_name = f'executor.{self.config.executor_uuid}'
                        self._channel.basic_consume(
                            queue=queue_name,
                            on_message_callback=self._on_message_received,
                            auto_ack=False
                        )
                else:
                    break

            except Exception as e:
                logger.error(f"消费循环出错: {e}", exc_info=True)
                if self._is_running:
                    time.sleep(5)
                else:
                    break

        logger.info("消费循环已结束")

    def stop(self):
        """停止消费者"""
        logger.info("正在停止消费者...")
        self._is_running = False

        if self._connection and not self._connection.is_closed:
            try:
                self._connection.close()
            except:
                pass

        if self._consumer_thread:
            self._consumer_thread.join(timeout=5)

        # 触发断开连接回调
        if self.on_disconnected:
            try:
                self.on_disconnected()
            except Exception as e:
                logger.error(f"断开连接回调出错: {e}")

        logger.info("消费者已停止")

    def is_running(self) -> bool:
        """是否正在运行"""
        return self._is_running and self._connection is not None


# 单例
_consumer: Optional[MessageQueueConsumer] = None


def get_message_queue_consumer() -> MessageQueueConsumer:
    """获取消息队列消费者单例"""
    global _consumer
    if _consumer is None:
        _consumer = MessageQueueConsumer()
    return _consumer
