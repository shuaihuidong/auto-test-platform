from django.db import models
from django.conf import settings


class Project(models.Model):
    """
    项目模型
    """
    TYPE_CHOICES = [
        ('web', 'Web自动化'),
        ('mobile', '移动端自动化'),
        ('api', 'API接口测试'),
    ]

    name = models.CharField(max_length=200, verbose_name='项目名称')
    description = models.TextField(blank=True, verbose_name='项目描述')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='web', verbose_name='项目类型')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'projects_project'
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def script_count(self):
        return self.scripts.count()

    @property
    def plan_count(self):
        return self.plans.count()
