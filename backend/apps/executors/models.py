from django.db import models
from django.conf import settings


class Executor(models.Model):
    """
    执行机模型
    """
    STATUS_CHOICES = [
        ('idle', '空闲'),
        ('online', '在线'),
        ('offline', '离线'),
        ('busy', '忙碌'),
        ('error', '异常'),
    ]

    SCOPE_CHOICES = [
        ('global', '全局可用'),
        ('project', '项目专用'),
    ]

    # 基本信息
    uuid = models.UUIDField(unique=True, verbose_name='执行机ID')
    name = models.CharField(max_length=200, verbose_name='执行机名称')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executors',
        verbose_name='所属用户'
    )

    # 状态信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name='状态')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='global', verbose_name='作用域')

    # 配置信息
    max_concurrent = models.IntegerField(default=3, verbose_name='最大并发数')
    current_tasks = models.IntegerField(default=0, verbose_name='当前任务数')
    browser_types = models.JSONField(default=list, verbose_name='支持的浏览器')  # ['chrome', 'firefox', 'edge']
    platform = models.CharField(max_length=50, verbose_name='操作系统')  # 'Windows', 'Mac', 'Linux'

    # 分组和标签
    groups = models.ManyToManyField(
        'ExecutorGroup',
        blank=True,
        related_name='executors',
        verbose_name='分组'
    )
    tags = models.ManyToManyField(
        'ExecutorTag',
        blank=True,
        related_name='executors',
        verbose_name='标签'
    )

    # 心跳信息
    last_heartbeat = models.DateTimeField(null=True, blank=True, verbose_name='最后心跳时间')
    version = models.CharField(max_length=50, blank=True, verbose_name='执行机版本')

    # 绑定的项目（项目专用模式）
    bound_projects = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='bound_executors',
        verbose_name='绑定项目'
    )

    # 是否启用
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')

    # 备注
    description = models.TextField(blank=True, verbose_name='描述')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'executors_executor'
        verbose_name = '执行机'
        verbose_name_plural = '执行机'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                name='unique_executor_name_per_owner',
                violation_error_message='同一用户下不能存在同名执行机'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'

    @property
    def is_online(self):
        """判断是否在线（心跳在2分钟内）"""
        from django.utils import timezone
        if not self.last_heartbeat:
            return False
        return (timezone.now() - self.last_heartbeat).total_seconds() < 120

    @property
    def is_available(self):
        """判断是否可用（在线 + 启用 + 未达并发上限）"""
        return self.is_online and self.is_enabled and self.current_tasks < self.max_concurrent


class ExecutorGroup(models.Model):
    """
    执行机分组模型
    """
    name = models.CharField(max_length=200, unique=True, verbose_name='分组名称')
    description = models.TextField(blank=True, verbose_name='描述')
    color = models.CharField(max_length=20, default='#1890ff', verbose_name='颜色标识')
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'executors_executorgroup'
        verbose_name = '执行机分组'
        verbose_name_plural = '执行机分组'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name


class ExecutorTag(models.Model):
    """
    执行机标签模型
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='标签名称')
    color = models.CharField(max_length=20, default='#52c41a', verbose_name='颜色标识')
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'executors_executortag'
        verbose_name = '执行机标签'
        verbose_name_plural = '执行机标签'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name


class ExecutorStatusLog(models.Model):
    """
    执行机状态日志
    """
    executor = models.ForeignKey(
        Executor,
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name='执行机'
    )
    status = models.CharField(max_length=20, verbose_name='状态')
    cpu_usage = models.FloatField(null=True, blank=True, verbose_name='CPU使用率')
    memory_usage = models.FloatField(null=True, blank=True, verbose_name='内存使用率')
    disk_usage = models.FloatField(null=True, blank=True, verbose_name='磁盘使用率')
    current_tasks = models.IntegerField(default=0, verbose_name='当前任务数')
    message = models.TextField(blank=True, verbose_name='消息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'executors_executorstatuslog'
        verbose_name = '执行机状态日志'
        verbose_name_plural = '执行机状态日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.executor.name} - {self.status}'


class Variable(models.Model):
    """
    变量管理模型
    支持项目级和脚本级变量
    """
    SCOPE_CHOICES = [
        ('project', '项目级'),
        ('script', '脚本级'),
    ]

    TYPE_CHOICES = [
        ('string', '字符串'),
        ('number', '数字'),
        ('boolean', '布尔值'),
        ('json', 'JSON对象'),
    ]

    name = models.CharField(max_length=200, verbose_name='变量名')
    value = models.JSONField(verbose_name='变量值')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='string', verbose_name='变量类型')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, verbose_name='作用域')

    # 关联对象（根据scope不同，关联不同的对象）
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='variables',
        verbose_name='所属项目'
    )
    script = models.ForeignKey(
        'scripts.Script',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='managed_variables',
        verbose_name='所属脚本'
    )

    # 描述
    description = models.TextField(blank=True, verbose_name='描述')

    # 是否敏感数据（如密码、token等，敏感数据在API中需要脱敏）
    is_sensitive = models.BooleanField(default=False, verbose_name='是否敏感')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_variables',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'executors_variable'
        verbose_name = '变量'
        verbose_name_plural = '变量'
        ordering = ['scope', 'project', 'script', 'name']
        unique_together = [['scope', 'project', 'script', 'name']]

    def __str__(self):
        return f'{self.name} = {self.value}'


class TaskQueue(models.Model):
    """
    任务队列模型
    用于管理待执行的任务
    """
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('assigned', '已分配'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]

    PRIORITY_CHOICES = [
        ('low', '低'),
        ('normal', '正常'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]

    # 关联信息
    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='执行记录'
    )
    executor = models.ForeignKey(
        Executor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='分配的执行机'
    )

    # 状态和优先级
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal', verbose_name='优先级')

    # 任务数据
    script_data = models.JSONField(verbose_name='脚本数据')

    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')

    # 时间信息
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name='分配时间')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'executors_taskqueue'
        verbose_name = '任务队列'
        verbose_name_plural = '任务队列'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f'Task {self.id} - {self.get_status_display()}'

    @property
    def duration(self):
        """执行时长"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return 0
