"""
清理 RabbitMQ 队列中的阻塞任务
"""

import sys
import pika
from pika import PlainCredentials, ConnectionParameters


def clear_queue(host='127.0.0.1', port=5672, username='guest', password='guest',
                vhost='/', queue_name=None):
    """
    清空指定队列

    Args:
        host: RabbitMQ 主机
        port: RabbitMQ 端口
        username: 用户名
        password: 密码
        vhost: 虚拟主机
        queue_name: 队列名称（如果为 None，将清空所有 executor.* 队列）
    """
    try:
        # 建立连接
        credentials = PlainCredentials(username, password)
        parameters = ConnectionParameters(
            host=host,
            port=port,
            virtual_host=vhost,
            credentials=credentials
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        if queue_name:
            # 清空指定队列
            queue_info = channel.queue_declare(queue=queue_name, passive=True)
            message_count = queue_info.method.message_count

            if message_count > 0:
                channel.queue_purge(queue=queue_name)
                print(f"[OK] 已清空队列: {queue_name} (移除了 {message_count} 条消息)")
            else:
                print(f"[OK] 队列为空: {queue_name}")
        else:
            # 从配置文件读取 executor_uuid
            try:
                from config import get_config_manager
                config = get_config_manager().get()
                full_queue_name = f'executor.{config.executor_uuid}'

                queue_info = channel.queue_declare(queue=full_queue_name, passive=True)
                message_count = queue_info.method.message_count

                if message_count > 0:
                    channel.queue_purge(queue=full_queue_name)
                    print(f"[OK] 已清空队列: {full_queue_name} (移除了 {message_count} 条消息)")
                else:
                    print(f"[OK] 队列为空: {full_queue_name}")

            except Exception as e:
                print(f"[ERROR] 无法读取配置: {e}")
                print("\n请手动指定队列名称，例如:")
                print(f"  python {sys.argv[0]} --queue executor.your-uuid-here")

        connection.close()
        print("\n清理完成!")

    except Exception as e:
        print(f"[ERROR] 清理失败: {e}")
        return False

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='清理 RabbitMQ 队列中的阻塞任务')
    parser.add_argument('--host', default='127.0.0.1', help='RabbitMQ 主机地址')
    parser.add_argument('--port', type=int, default=5672, help='RabbitMQ 端口')
    parser.add_argument('--username', default='guest', help='RabbitMQ 用户名')
    parser.add_argument('--password', default='guest', help='RabbitMQ 密码')
    parser.add_argument('--vhost', default='/', help='RabbitMQ 虚拟主机')
    parser.add_argument('--queue', help='指定队列名称（可选）')

    args = parser.parse_args()

    print("=" * 50)
    print("  RabbitMQ Queue Cleaner")
    print("=" * 50)
    print()

    clear_queue(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        vhost=args.vhost,
        queue_name=args.queue
    )
