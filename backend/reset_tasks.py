import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from apps.executors.models import TaskQueue, Executor

# Reset all assigned and running tasks
TaskQueue.objects.filter(status__in=['assigned', 'running']).update(
    status='pending',
    executor=None,
    assigned_at=None
)
print('Tasks reset to pending')

# Reset executor count
exec = Executor.objects.filter(name__contains='01').first()
if exec:
    exec.current_tasks = 0
    exec.save()
    print('Executor current_tasks reset to 0')

# Check pending tasks with plan_scripts
pending = TaskQueue.objects.filter(status='pending')
print('Total pending tasks:', pending.count())

# Show sample task data
if pending.exists():
    task = pending.first()
    sd = task.script_data
    print('Sample task:')
    print('  parent_execution_id:', sd.get('parent_execution_id'))
    print('  plan_scripts count:', len(sd.get('plan_scripts', [])))
    print('  script_index:', sd.get('script_index'))
