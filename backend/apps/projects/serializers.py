from rest_framework import serializers
from .models import Project, ProjectMember


class ProjectMemberSerializer(serializers.ModelSerializer):
    """项目成员序列化器 - 用于列表展示"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_owner = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'user_id', 'username', 'email', 'role', 'joined_at', 'is_owner']
        read_only_fields = ['id', 'joined_at', 'is_owner']


class ProjectMemberCreateSerializer(serializers.ModelSerializer):
    """项目成员创建序列化器"""
    class Meta:
        model = ProjectMember
        fields = ['user', 'role']

    def validate_user(self, value):
        """验证用户是否已是项目成员"""
        project = self.context['project']
        if ProjectMember.objects.filter(project=project, user=value).exists():
            raise serializers.ValidationError('该用户已是项目成员')
        return value


class ProjectSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    script_count = serializers.IntegerField(read_only=True)
    plan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'creator', 'creator_name',
                  'script_count', 'plan_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
