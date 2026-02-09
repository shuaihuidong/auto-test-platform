from rest_framework import serializers
from .models import Plan


class PlanSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    script_count = serializers.IntegerField(read_only=True)
    scripts_detail = serializers.SerializerMethodField(read_only=True)
    schedule_type_display = serializers.CharField(source='get_schedule_type_display', read_only=True)
    execution_mode_display = serializers.CharField(source='get_execution_mode_display', read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'project', 'project_name', 'name', 'description', 'script_ids',
                  'script_count', 'scripts_detail', 'schedule_type', 'schedule_type_display',
                  'cron_expression', 'schedule_enabled', 'execution_mode', 'execution_mode_display',
                  'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        # 验证计划名称在同一项目下的唯一性
        project = attrs.get('project')
        name = attrs.get('name')

        if project and name:
            # 检查是否是更新操作
            instance = self.instance
            queryset = Plan.objects.filter(project=project, name=name)

            # 如果是更新操作，排除当前实例
            if instance:
                queryset = queryset.exclude(id=instance.id)

            if queryset.exists():
                raise serializers.ValidationError({
                    'name': '同一项目下已存在同名计划'
                })

        return attrs

    def get_scripts_detail(self, obj):
        from apps.scripts.models import Script
        if not obj.script_ids:
            return []
        scripts = Script.objects.filter(id__in=obj.script_ids)
        return [{'id': s.id, 'name': s.name, 'type': s.type, 'framework': s.framework} for s in scripts]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
