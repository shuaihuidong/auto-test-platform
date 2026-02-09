from apps.executions.models import Execution

e = Execution.objects.last()
print(f'ID: {e.id}')
print(f'Type: {e.execution_type}')
print(f'Parent: {e.parent_id}')
print(f'Plan: {e.plan_id}')
print(f'Script: {e.script_id}')
print(f'Children: {list(e.children.values_list("id", flat=True))}')
