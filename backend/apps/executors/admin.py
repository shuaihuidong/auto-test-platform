from django.contrib import admin
from .models import Executor, ExecutorGroup, ExecutorTag, ExecutorStatusLog, Variable, TaskQueue


@admin.register(ExecutorGroup)
class ExecutorGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'sort_order', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['color', 'sort_order']


@admin.register(ExecutorTag)
class ExecutorTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'sort_order', 'created_at']
    search_fields = ['name']
    list_editable = ['color', 'sort_order']


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'scope', 'platform', 'current_tasks', 'max_concurrent', 'last_heartbeat', 'is_enabled']
    list_filter = ['status', 'scope', 'platform', 'is_enabled']
    search_fields = ['name', 'uuid', 'owner__username']
    filter_horizontal = ['groups', 'tags', 'bound_projects']
    readonly_fields = ['uuid', 'last_heartbeat', 'created_at', 'updated_at']


@admin.register(ExecutorStatusLog)
class ExecutorStatusLogAdmin(admin.ModelAdmin):
    list_display = ['executor', 'status', 'current_tasks', 'cpu_usage', 'memory_usage', 'created_at']
    list_filter = ['status']
    search_fields = ['executor__name']
    readonly_fields = ['created_at']


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'scope', 'project', 'script', 'type', 'is_sensitive', 'created_by', 'created_at']
    list_filter = ['scope', 'type', 'is_sensitive']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskQueue)
class TaskQueueAdmin(admin.ModelAdmin):
    list_display = ['id', 'execution', 'executor', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['execution__script__name']
    readonly_fields = ['created_at']
