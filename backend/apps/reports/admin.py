from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'execution', 'pass_rate', 'total_duration', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    search_fields = ['execution__plan__name', 'execution__script__name']
