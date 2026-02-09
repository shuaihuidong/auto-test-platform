from rest_framework import serializers
from .models import Execution


class ExecutionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    script_name = serializers.CharField(source='script.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    duration = serializers.IntegerField(read_only=True)
    passed_count = serializers.IntegerField(read_only=True)
    failed_count = serializers.IntegerField(read_only=True)
    total_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    execution_type_display = serializers.CharField(source='get_execution_type_display', read_only=True)
    execution_mode_display = serializers.CharField(source='get_execution_mode_display', read_only=True)
    children_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Execution
        fields = ['id', 'execution_type', 'execution_type_display', 'execution_mode', 'execution_mode_display',
                  'parent', 'plan', 'plan_name', 'script', 'script_name', 'status', 'status_display',
                  'result', 'duration', 'passed_count', 'failed_count', 'total_count',
                  'children_count', 'started_at', 'completed_at', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'started_at', 'completed_at', 'created_at']

    def get_children_count(self, obj):
        return obj.children.count() if obj.execution_type == 'plan' else 0

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExecutionCreateSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(required=False)
    script_id = serializers.IntegerField(required=False)
    executor_id = serializers.IntegerField(required=False, allow_null=True)
    execution_mode = serializers.ChoiceField(
        choices=['sequential', 'parallel'],
        default='parallel',
        required=False
    )

    def validate(self, attrs):
        if not attrs.get('plan_id') and not attrs.get('script_id'):
            raise serializers.ValidationError("必须提供plan_id或script_id")

        # 如果是计划执行，从计划中获取执行模式（如果未指定）
        plan_id = attrs.get('plan_id')
        if plan_id and not attrs.get('execution_mode'):
            from apps.plans.models import Plan
            try:
                plan = Plan.objects.get(id=plan_id)
                attrs['execution_mode'] = plan.execution_mode
            except Plan.DoesNotExist:
                attrs['execution_mode'] = 'parallel'

        return attrs
