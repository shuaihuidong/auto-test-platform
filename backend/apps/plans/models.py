from django.db import models
from django.conf import settings


class Plan(models.Model):
    """
    测试计划模型
    """
    SCHEDULE_TYPE_CHOICES = [
        ('manual', '手动执行'),
        ('cron', '定时执行'),
    ]

    EXECUTION_MODE_CHOICES = [
        ('sequential', '顺序执行'),
        ('parallel', '并行执行'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='plans',
        verbose_name='所属项目'
    )
    name = models.CharField(max_length=200, verbose_name='计划名称')
    description = models.TextField(blank=True, verbose_name='描述')
    script_ids = models.JSONField(default=list, verbose_name='包含的脚本列表')
    schedule_type = models.CharField(
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        default='manual',
        verbose_name='执行方式'
    )
    cron_expression = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Cron表达式',
        help_text='例如: 0 2 * * * 表示每天凌晨2点执行'
    )
    schedule_enabled = models.BooleanField(
        default=True,
        verbose_name='启用调度'
    )
    execution_mode = models.CharField(
        max_length=20,
        choices=EXECUTION_MODE_CHOICES,
        default='parallel',
        verbose_name='执行模式'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_plans',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'plans_plan'
        verbose_name = '测试计划'
        verbose_name_plural = '测试计划'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'name'],
                name='unique_plan_name_per_project',
                violation_error_message='同一项目下不能存在同名计划'
            )
        ]

    def __str__(self):
        return self.name

    @property
    def script_count(self):
        return len(self.script_ids) if isinstance(self.script_ids, list) else 0
