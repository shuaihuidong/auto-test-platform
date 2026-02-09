from django.db import models


class Report(models.Model):
    """
    测试报告模型
    """
    execution = models.OneToOneField(
        'executions.Execution',
        on_delete=models.CASCADE,
        related_name='report',
        verbose_name='关联执行'
    )
    summary = models.JSONField(default=dict, verbose_name='汇总数据')
    # summary 格式: {"pass_rate": 80, "total_duration": 120, "trend_data": [...]}
    html_report = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='HTML报告路径'
    )
    pdf_report = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='PDF报告路径'
    )
    charts_data = models.JSONField(default=dict, verbose_name='图表数据')
    # charts_data 格式: {"trend": [...], "distribution": [...], "failure_analysis": [...]}
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='生成时间')

    class Meta:
        db_table = 'reports_report'
        verbose_name = '测试报告'
        verbose_name_plural = '测试报告'
        ordering = ['-created_at']

    def __str__(self):
        return f'Report for Execution {self.execution_id}'

    @property
    def pass_rate(self):
        return self.summary.get('pass_rate', 0)

    @property
    def total_duration(self):
        return self.summary.get('total_duration', 0)


class TrendAnalysis(models.Model):
    """
    趋势分析模型
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='trend_analyses',
        verbose_name='所属项目'
    )
    script = models.ForeignKey(
        'scripts.Script',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='trend_analyses',
        verbose_name='关联脚本'
    )
    date = models.DateField(verbose_name='日期')
    total_executions = models.IntegerField(default=0, verbose_name='总执行次数')
    successful_executions = models.IntegerField(default=0, verbose_name='成功次数')
    failed_executions = models.IntegerField(default=0, verbose_name='失败次数')
    pass_rate = models.FloatField(default=0, verbose_name='通过率')
    avg_duration = models.FloatField(default=0, verbose_name='平均耗时(秒)')

    class Meta:
        db_table = 'reports_trendanalysis'
        verbose_name = '趋势分析'
        verbose_name_plural = '趋势分析'
        ordering = ['-date']
        unique_together = [['project', 'script', 'date']]

    def __str__(self):
        return f'{self.project.name} - {self.date}'


class FailureAnalysis(models.Model):
    """
    失败分析模型
    """
    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.CASCADE,
        related_name='failure_analyses',
        verbose_name='关联执行'
    )
    step_index = models.IntegerField(verbose_name='步骤索引')
    step_name = models.CharField(max_length=200, verbose_name='步骤名称')
    error_type = models.CharField(max_length=100, verbose_name='错误类型')
    error_message = models.TextField(verbose_name='错误消息')
    frequency = models.IntegerField(default=1, verbose_name='出现频次')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'reports_failureanalysis'
        verbose_name = '失败分析'
        verbose_name_plural = '失败分析'
        ordering = ['-frequency', '-created_at']

    def __str__(self):
        return f'{self.step_name} - {self.error_type}'


class Screenshot(models.Model):
    """
    截图模型
    用于存储执行过程中的截图
    """
    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.CASCADE,
        related_name='screenshots',
        verbose_name='关联执行'
    )
    step_index = models.IntegerField(verbose_name='步骤索引')
    step_name = models.CharField(max_length=200, blank=True, verbose_name='步骤名称')
    image_path = models.CharField(max_length=500, verbose_name='图片路径')
    thumbnail_path = models.CharField(max_length=500, blank=True, verbose_name='缩略图路径')
    is_error = models.BooleanField(default=False, verbose_name='是否错误截图')
    error_message = models.TextField(blank=True, verbose_name='错误消息')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'reports_screenshot'
        verbose_name = '截图'
        verbose_name_plural = '截图'
        ordering = ['step_index', '-timestamp']

    def __str__(self):
        return f'{self.execution_id} - Step {self.step_index}'
