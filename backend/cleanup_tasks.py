import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_test_platform.settings')
django.setup()

from apps.executors.models import TaskQueue, Executor
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(hours=1)
old_tasks = TaskQueue.objects.filter(
    status__in=['assigned', 'running'],
    created_at__lt=cutoff
)
cnt = old_tasks.count()
print('Old tasks: {}'.format(cnt))
old_tasks.update(status='cancelled')

exec = Executor.objects.filter(name__contains='01').first()
if exec:
    exec.current_tasks = 0
    exec.save()
    print('Executor reset done')
