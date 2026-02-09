from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    execution_status = serializers.CharField(source='execution.status', read_only=True)
    execution_plan_name = serializers.CharField(source='execution.plan.name', read_only=True)
    execution_script_name = serializers.CharField(source='execution.script.name', read_only=True)
    execution_type = serializers.CharField(source='execution.execution_type', read_only=True)
    pass_rate = serializers.FloatField(read_only=True)
    total_duration = serializers.IntegerField(read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'execution', 'execution_status', 'execution_plan_name',
                  'execution_script_name', 'execution_type', 'summary', 'html_report', 'charts_data',
                  'pass_rate', 'total_duration', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChartDataSerializer(serializers.Serializer):
    """图表数据序列化器"""
    trend = serializers.ListField(required=False)
    distribution = serializers.ListField(required=False)
    failure_analysis = serializers.ListField(required=False)
    history = serializers.ListField(required=False)
