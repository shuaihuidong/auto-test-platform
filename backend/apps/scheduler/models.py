"""
定时任务应用
"""
from django.db import models
from django.conf import settings


class ScheduledTask(models.Model):
    """
    定时任务模型
    """
    STATUS_CHOICES = [
        ('enabled', '启用'),
        ('disabled', '禁用'),
        ('running', '运行中'),
        ('paused', '已暂停'),
    ]

    SCHEDULE_TYPE_CHOICES = [
        ('interval', '间隔执行'),
        ('cron', 'Cron表达式'),
        ('once', '一次性'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='scheduled_tasks',
        verbose_name='所属项目'
    )
    name = models.CharField(max_length=200, verbose_name='任务名称')
    description = models.TextField(blank=True, verbose_name='描述')

    # 关联脚本或计划
    script = models.ForeignKey(
        'scripts.Script',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='scheduled_tasks',
        verbose_name='关联脚本'
    )
    plan = models.ForeignKey(
        'plans.Plan',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='scheduled_tasks',
        verbose_name='关联计划'
    )

    # 调度配置
    schedule_type = models.CharField(
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        default='interval',
        verbose_name='调度类型'
    )
    schedule_config = models.JSONField(default=dict, verbose_name='调度配置')
    # 间隔执行: {"interval": 3600, "unit": "seconds"}
    # Cron: {"cron": "0 0 * * *"}
    # 一次性: {"execute_at": "2024-01-01 00:00:00"}

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enabled',
        verbose_name='状态'
    )

    # 执行配置
    execute_on_failure = models.BooleanField(default=False, verbose_name='失败时是否通知')
    notification_config = models.JSONField(default=dict, verbose_name='通知配置')

    # 统计信息
    last_execution = models.DateTimeField(null=True, blank=True, verbose_name='上次执行时间')
    next_execution = models.DateTimeField(null=True, blank=True, verbose_name='下次执行时间')
    total_executions = models.IntegerField(default=0, verbose_name='总执行次数')
    successful_executions = models.IntegerField(default=0, verbose_name='成功次数')
    failed_executions = models.IntegerField(default=0, verbose_name='失败次数')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_scheduled_tasks',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'scheduler_scheduledtask'
        verbose_name = '定时任务'
        verbose_name_plural = '定时任务'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def calculate_next_execution(self):
        """计算下次执行时间"""
        from datetime import datetime, timedelta
        from croniter import croniter

        now = datetime.now()

        if self.schedule_type == 'interval':
            config = self.schedule_config
            interval = config.get('interval', 3600)
            unit = config.get('unit', 'seconds')

            # 转换为秒
            if unit == 'minutes':
                interval *= 60
            elif unit == 'hours':
                interval *= 3600
            elif unit == 'days':
                interval *= 86400

            if self.last_execution:
                self.next_execution = self.last_execution + timedelta(seconds=interval)
            else:
                self.next_execution = now + timedelta(seconds=interval)

        elif self.schedule_type == 'cron':
            cron_expr = self.schedule_config.get('cron', '0 0 * * *')
            base = self.last_execution if self.last_execution else now
            cron = croniter(cron_expr, base)
            self.next_execution = cron.get_next(datetime)

        elif self.schedule_type == 'once':
            execute_at_str = self.schedule_config.get('execute_at')
            if execute_at_str:
                from django.utils.dateparse import parse_datetime
                self.next_execution = parse_datetime(execute_at_str)

        self.save()
        return self.next_execution

    def update_execution_stats(self, success):
        """更新执行统计"""
        self.total_executions += 1
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        self.last_execution = timezone.now()
        self.calculate_next_execution()
        self.save()


class ScheduledTaskLog(models.Model):
    """
    定时任务执行日志
    """
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('skipped', '跳过'),
    ]

    scheduled_task = models.ForeignKey(
        ScheduledTask,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='关联任务'
    )
    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scheduled_logs',
        verbose_name='执行记录'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='状态')
    message = models.TextField(blank=True, verbose_name='消息')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    duration = models.IntegerField(null=True, blank=True, verbose_name='耗时(秒)')

    class Meta:
        db_table = 'scheduler_scheduledtasklog'
        verbose_name = '定时任务日志'
        verbose_name_plural = '定时任务日志'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.scheduled_task.name} - {self.started_at}'
