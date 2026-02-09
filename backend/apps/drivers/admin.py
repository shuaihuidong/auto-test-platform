from django.contrib import admin
from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['framework', 'browser', 'version', 'is_recommended', 'created_at']
    list_filter = ['framework', 'browser', 'is_recommended']
    search_fields = ['description']
