from rest_framework import serializers
from .models import Driver


class DriverSerializer(serializers.ModelSerializer):
    framework_display = serializers.CharField(source='get_framework_display', read_only=True)
    browser_display = serializers.CharField(source='get_browser_display', read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'framework', 'framework_display', 'browser', 'browser_display',
                  'version', 'download_url', 'install_command', 'is_recommended',
                  'description', 'created_at']
        read_only_fields = ['id', 'created_at']
