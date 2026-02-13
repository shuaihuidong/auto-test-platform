from rest_framework import serializers
from .models import Executor, ExecutorGroup, ExecutorTag, ExecutorStatusLog, Variable, TaskQueue
from apps.projects.models import Project
from apps.scripts.models import Script


class ExecutorTagSerializer(serializers.ModelSerializer):
    """执行机标签序列化器"""

    class Meta:
        model = ExecutorTag
        fields = ['id', 'name', 'color', 'sort_order']

class ExecutorGroupSerializer(serializers.ModelSerializer):
    """执行机分组序列化器"""

    class Meta:
        model = ExecutorGroup
        fields = ['id', 'name', 'description', 'color', 'sort_order']

class ExecutorStatusLogSerializer(serializers.ModelSerializer):
    """执行机状态日志序列化器"""

    class Meta:
        model = ExecutorStatusLog
        fields = ['id', 'status', 'cpu_usage', 'memory_usage', 'disk_usage',
                  'current_tasks', 'message', 'created_at']

class ExecutorSerializer(serializers.ModelSerializer):
    """执行机序列化器"""

    groups = ExecutorGroupSerializer(many=True, read_only=True)
    tags = ExecutorTagSerializer(many=True, read_only=True)
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    bound_project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    bound_projects = serializers.SerializerMethodField()

    owner_name = serializers.CharField(source='owner.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    is_online = serializers.BooleanField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Executor
        fields = [
            'id', 'uuid', 'name', 'owner', 'owner_name', 'status', 'status_display',
            'scope', 'scope_display', 'max_concurrent', 'current_tasks',
            'browser_types', 'platform', 'groups', 'group_ids', 'tags', 'tag_ids',
            'bound_projects', 'bound_project_ids', 'last_heartbeat', 'version',
            'is_enabled', 'description', 'is_online', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'owner', 'last_heartbeat', 'created_at', 'updated_at']

    def validate(self, attrs):
        # 验证执行机名称在同一用户下的唯一性
        name = attrs.get('name')

        if name:
            # 获取当前请求的用户
            user = self.context['request'].user

            # 检查是否是更新操作
            instance = self.instance
            queryset = Executor.objects.filter(owner=user, name=name)

            # 如果是更新操作，排除当前实例
            if instance:
                queryset = queryset.exclude(id=instance.id)

            if queryset.exists():
                raise serializers.ValidationError({
                    'name': '同一用户下已存在同名执行机'
                })

        return attrs

    def get_bound_projects(self, obj):
        return [{'id': p.id, 'name': p.name} for p in obj.bound_projects.all()]

    def create(self, validated_data):
        group_ids = validated_data.pop('group_ids', [])
        tag_ids = validated_data.pop('tag_ids', [])
        bound_project_ids = validated_data.pop('bound_project_ids', [])

        # 生成 UUID
        import uuid
        validated_data['uuid'] = uuid.uuid4()

        executor = Executor.objects.create(**validated_data)
        if group_ids:
            executor.groups.set(group_ids)
        if tag_ids:
            executor.tags.set(tag_ids)
        if bound_project_ids:
            executor.bound_projects.set(bound_project_ids)

        return executor

    def validate_max_concurrent(self, value):
        """验证并发数上限"""
        if value < 1:
            raise serializers.ValidationError("并发数必须大于0")
        if value > 3:
            raise serializers.ValidationError("并发数上限为3")
        return value

    def __init__(self, *args, **kwargs):
        """让 platform 字段在更新时变为可选"""
        super().__init__(*args, **kwargs)
        # 如果是更新操作，platform 不需要提交
        if self.instance:
            self.fields['platform'].required = False

    def update(self, instance, validated_data):
        # 先提取这些字段（支持空数组的情况）
        group_ids = validated_data.pop('group_ids', None)
        tag_ids = validated_data.pop('tag_ids', None)
        bound_project_ids = validated_data.pop('bound_project_ids', None)

        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新多对多关系（包括清空的情况）
        if group_ids is not None:
            instance.groups.set(group_ids)
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        if bound_project_ids is not None:
            instance.bound_projects.set(bound_project_ids)

        return instance


class VariableSerializer(serializers.ModelSerializer):
    """变量序列化器"""

    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    creator_name = serializers.CharField(source='created_by.username', read_only=True)

    # 使用 JSONField 同时支持读写，并通过 to_representation 处理脱敏
    value = serializers.JSONField()

    class Meta:
        model = Variable
        fields = [
            'id', 'name', 'value', 'type', 'type_display', 'scope', 'scope_display',
            'project', 'script', 'description', 'is_sensitive', 'created_by',
            'creator_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """在序列化时对敏感数据进行脱敏处理"""
        data = super().to_representation(instance)
        if instance.is_sensitive:
            data['value'] = '******'
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskQueueSerializer(serializers.ModelSerializer):
    """任务队列序列化器"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    executor_info = ExecutorSerializer(source='executor', read_only=True)
    script_name = serializers.CharField(source='execution.script.name', read_only=True)
    project_name = serializers.CharField(source='execution.script.project.name', read_only=True)
    duration = serializers.IntegerField(read_only=True)

    class Meta:
        model = TaskQueue
        fields = [
            'id', 'execution', 'executor', 'executor_info', 'status', 'status_display',
            'priority', 'priority_display', 'script_data', 'error_message',
            'assigned_at', 'started_at', 'completed_at', 'duration', 'script_name',
            'project_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class ExecutorHeartbeatSerializer(serializers.Serializer):
    """执行机心跳序列化器"""

    status = serializers.CharField(required=False)
    current_tasks = serializers.IntegerField(required=False, default=0)
    cpu_usage = serializers.FloatField(required=False, allow_null=True)
    memory_usage = serializers.FloatField(required=False, allow_null=True)
    disk_usage = serializers.FloatField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_blank=True)


class ExecutorRegisterSerializer(serializers.Serializer):
    """执行机注册序列化器"""

    uuid = serializers.UUIDField(required=False)
    name = serializers.CharField(max_length=200)
    platform = serializers.CharField(max_length=50)
    browser_types = serializers.ListField(child=serializers.CharField())
    version = serializers.CharField(max_length=50, required=False, allow_blank=True)
    max_concurrent = serializers.IntegerField(default=3)
    description = serializers.CharField(required=False, allow_blank=True)


class TaskExecutionSerializer(serializers.Serializer):
    """任务执行序列化器"""

    task_id = serializers.IntegerField()
    result = serializers.JSONField()
    logs = serializers.ListField(child=serializers.DictField(), required=False)
    screenshots = serializers.ListField(child=serializers.DictField(), required=False)
