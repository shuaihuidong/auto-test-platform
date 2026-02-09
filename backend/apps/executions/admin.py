from django.contrib import admin
from .models import Execution


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ['id', 'plan', 'script', 'status', 'passed_count', 'failed_count', 'duration', 'created_by']
    list_filter = ['status', 'created_at']
    search_fields = ['plan__name', 'script__name']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
