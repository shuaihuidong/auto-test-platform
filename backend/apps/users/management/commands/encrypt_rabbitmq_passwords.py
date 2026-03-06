"""
加密现有的RabbitMQ密码

使用方法：
python manage.py encrypt_rabbitmq_passwords
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.views import encrypt_rabbitmq_password


class Command(BaseCommand):
    help = '加密数据库中现有的RabbitMQ密码'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='仅模拟运行，不实际修改数据库',
        )

    def handle(self, *args, **options):
        User = get_user_model()

        # 查找所有启用了RabbitMQ且有密码的用户
        users = User.objects.filter(
            rabbitmq_enabled=True,
            rabbitmq_password__isnull=False
        )

        if not users.exists():
            self.stdout.write(
                self.style.WARNING('没有找到需要加密的RabbitMQ密码')
            )
            return

        self.stdout.write(f'找到 {users.count()} 个用户的RabbitMQ密码需要处理')

        success_count = 0
        error_count = 0

        for user in users:
            try:
                # 检查密码是否已经被加密
                # 如果密码长度大于100，很可能是已加密的（加密后长度会变长）
                if len(user.rabbitmq_password) > 100:
                    self.stdout.write(
                        self.style.WARNING(f'用户 {user.username} 的密码似乎已加密，跳过')
                    )
                    continue

                # 加密密码
                encrypted_password = encrypt_rabbitmq_password(user.rabbitmq_password)

                if options['dry_run']:
                    self.stdout.write(
                        self.style.WARNING(f'[DRY RUN] 将加密用户 {user.username} 的密码')
                    )
                else:
                    user.rabbitmq_password = encrypted_password
                    user.save(update_fields=['rabbitmq_password'])
                    self.stdout.write(
                        self.style.SUCCESS(f'成功加密用户 {user.username} 的密码')
                    )

                success_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'加密用户 {user.username} 的密码失败: {str(e)}')
                )
                error_count += 1

        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'处理完成：成功 {success_count} 个，失败 {error_count} 个')

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('这是模拟运行，数据库未实际修改')
            )
            self.stdout.write('移除 --dry-run 参数以实际执行加密')
