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

        # 【关键修复】缓存已停止的父执行ID，避免重复查询和意外执行旧任务
        # 使用列表存储（保留顺序，方便清理旧条目）
        self._stopped_parent_executions: list = []
        self._stopped_cache_lock = threading.Lock()
        # 缓存大小限制，避免无限增长（保留最近100个已停止的执行）
        self._stopped_cache_max_size = 100

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
            logger.info(f"收到任务: {task_id}")

            # 【关键修复】在处理消息之前，先检查任务是否已被停止
            # 如果任务已被停止，直接 NACK 不重新入队，不调用 on_task_received
            if self._is_task_stopped(message):
                logger.warning(f"任务 {task_id} 已被停止，直接 NACK 不重新入队")
                channel.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=False  # 不重新入队
                )
                return

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
                        # 任务被拒绝，需要判断是否重新入队
                        # 检查任务是否已被停止，如果停止则不重新入队
                        should_requeue = self._should_requeue_task(message)

                        channel.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=should_requeue  # 根据任务状态决定是否重新入队
                        )

                        if should_requeue:
                            logger.warning(f"任务 {task_id} 被拒绝（并发限制），已 NACK 重新入队")
                        else:
                            logger.warning(f"任务 {task_id} 已被停止，已 NACK 不再重新入队")

                except Exception as e:
                    logger.error(f"处理任务时出错: {e}", exc_info=True)
                    # 发生异常，NACK 并重新入队
                    try:
                        channel.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=True
                        )
                    except:
                        pass
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

    def _is_task_stopped(self, message: dict) -> bool:
        """
        检查任务是否已被停止

        在接收消息的最初阶段就检查，避免处理已停止的任务

        Args:
            message: 任务消息

        Returns:
            任务是否已被停止（True=已停止，False=未停止）
        """
        try:
            script_data = message.get("script_data", {})
            parent_execution_id = script_data.get("parent_execution_id")
            execution_id = message.get("execution_id", "")

            if not parent_execution_id and not execution_id:
                # 没有执行ID，可能是旧格式的消息
                return False

            # 【关键修复】先检查本地缓存，避免重复查询
            with self._stopped_cache_lock:
                if parent_execution_id in self._stopped_parent_executions:
                    logger.info(f"[停止检查-缓存] 父任务 {parent_execution_id} 已停止（缓存命中），拒绝接收任务")
                    return True

            import requests
            api_base = self.config.server_url.rstrip('/')

            # 优先检查父任务状态
            if parent_execution_id:
                try:
                    status_check_url = f"{api_base}/api/executions/{parent_execution_id}/status_check/"
                    response = requests.get(status_check_url, timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        parent_status = data.get("status", "")
                        if parent_status == "stopped":
                            # 【关键修复】将已确认停止的父执行ID加入缓存
                            with self._stopped_cache_lock:
                                if parent_execution_id not in self._stopped_parent_executions:
                                    self._stopped_parent_executions.append(parent_execution_id)
                                    # 如果缓存超过限制，移除最旧的条目
                                    if len(self._stopped_parent_executions) > self._stopped_cache_max_size:
                                        self._stopped_parent_executions.pop(0)
                            logger.info(f"[停止检查] 父任务 {parent_execution_id} 已停止，加入缓存并拒绝接收任务")
                            return True
                except:
                    pass  # 查询失败，继续处理

            # 检查子执行状态
            if execution_id:
                try:
                    status_check_url = f"{api_base}/api/executions/{execution_id}/status_check/"
                    response = requests.get(status_check_url, timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        exec_status = data.get("status", "")
                        if exec_status == "stopped":
                            logger.info(f"[停止检查] 执行 {execution_id} 已停止，拒绝接收任务")
                            return True
                except:
                    pass  # 查询失败，继续处理

            # 默认任务未停止
            return False

        except Exception as e:
            logger.debug(f"检查任务停止状态时出错: {e}")
            return False

    def _should_requeue_task(self, message: dict) -> bool:
        """
        判断被拒绝的任务是否应该重新入队

        如果任务已被停止（父任务或子任务状态为 stopped），则不重新入队

        Args:
            message: 任务消息

        Returns:
            是否应该重新入队
        """
        try:
            script_data = message.get("script_data", {})
            parent_execution_id = script_data.get("parent_execution_id")
            execution_id = message.get("execution_id", "")

            if not parent_execution_id and not execution_id:
                # 没有执行ID，可能是旧格式的消息，保守处理重新入队
                return True

            # 【关键修复】先检查本地缓存
            with self._stopped_cache_lock:
                if parent_execution_id in self._stopped_parent_executions:
                    logger.info(f"[停止检查-缓存] 父任务 {parent_execution_id} 已停止（缓存命中），任务不重新入队")
                    return False

            import requests
            api_base = self.config.server_url.rstrip('/')

            # 优先检查父任务状态
            if parent_execution_id:
                try:
                    status_check_url = f"{api_base}/api/executions/{parent_execution_id}/status_check/"
                    response = requests.get(status_check_url, timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        parent_status = data.get("status", "")
                        if parent_status == "stopped":
                            # 【关键修复】将已确认停止的父执行ID加入缓存
                            with self._stopped_cache_lock:
                                if parent_execution_id not in self._stopped_parent_executions:
                                    self._stopped_parent_executions.append(parent_execution_id)
                                    # 如果缓存超过限制，移除最旧的条目
                                    if len(self._stopped_parent_executions) > self._stopped_cache_max_size:
                                        self._stopped_parent_executions.pop(0)
                            logger.info(f"父任务 {parent_execution_id} 已停止，加入缓存且任务不重新入队")
                            return False
                except:
                    pass  # 查询失败，保守处理

            # 检查子执行状态
            if execution_id:
                try:
                    status_check_url = f"{api_base}/api/executions/{execution_id}/status_check/"
                    response = requests.get(status_check_url, timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        exec_status = data.get("status", "")
                        if exec_status == "stopped":
                            logger.info(f"执行 {execution_id} 已停止，任务不重新入队")
                            return False
                except:
                    pass  # 查询失败，保守处理

            # 默认重新入队
            return True

        except Exception as e:
            logger.debug(f"检查任务状态时出错: {e}")
            return True

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
