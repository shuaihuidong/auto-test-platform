import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.executions.models import Execution

print('Total:', Execution.objects.count())
print('Plan executions:', Execution.objects.filter(execution_type='plan').count())
print('Script executions:', Execution.objects.filter(execution_type='script').count())

# 查看所有父执行记录
print('\n=== Parent executions (no parent) ===')
for e in Execution.objects.filter(parent__isnull=True).order_by('-id')[:5]:
    print(f'ID: {e.id}, Type: {e.execution_type}, Plan: {e.plan_id}, Script: {e.script_id}')

# 查看所有子执行记录
print('\n=== Child executions (has parent) ===')
for e in Execution.objects.filter(parent__isnull=False).order_by('-id')[:5]:
    print(f'ID: {e.id}, Parent: {e.parent_id}, Script: {e.script_id}')
