from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自定义用户模型 - 权限分级
    """
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('admin', '管理员'),
        ('tester', '测试人员'),
        ('guest', '访客'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest', verbose_name='角色')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    rabbitmq_password = models.CharField(max_length=100, null=True, blank=True, verbose_name='RabbitMQ密码')
    rabbitmq_enabled = models.BooleanField(default=False, verbose_name='启用RabbitMQ')

    class Meta:
        db_table = 'users_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']

    def __str__(self):
        return self.username
