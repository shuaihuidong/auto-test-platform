from django.db import models


class Driver(models.Model):
    """
    驱动/浏览器模型
    """
    FRAMEWORK_CHOICES = [
        ('selenium', 'Selenium'),
        ('playwright', 'Playwright'),
        ('appium', 'Appium'),
    ]

    BROWSER_CHOICES = [
        ('chrome', 'Chrome'),
        ('firefox', 'Firefox'),
        ('edge', 'Edge'),
        ('safari', 'Safari'),
        ('android', 'Android'),
        ('ios', 'iOS'),
    ]

    framework = models.CharField(max_length=20, choices=FRAMEWORK_CHOICES, verbose_name='框架')
    browser = models.CharField(max_length=20, choices=BROWSER_CHOICES, verbose_name='浏览器/平台')
    version = models.CharField(max_length=50, blank=True, verbose_name='版本')
    download_url = models.URLField(blank=True, verbose_name='下载地址')
    install_command = models.TextField(blank=True, verbose_name='安装命令')
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐')
    description = models.TextField(blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'drivers_driver'
        verbose_name = '驱动'
        verbose_name_plural = '驱动'
        ordering = ['framework', 'browser']

    def __str__(self):
        return f'{self.get_framework_display()} - {self.get_browser_display()}'
