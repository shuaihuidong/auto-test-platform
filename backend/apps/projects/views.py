from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, ProjectMember
from .serializers import ProjectSerializer, ProjectMemberSerializer, ProjectMemberCreateSerializer


class ProjectMemberViewSet(viewsets.ModelViewSet):
    """项目成员管理视图集"""
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取项目成员列表"""
        project_id = self.kwargs.get('project_pk')
        return ProjectMember.objects.filter(project_id=project_id).select_related('user')

    def get_serializer_context(self):
        """将项目传递给序列化器"""
        context = super().get_serializer_context()
        project_id = self.kwargs.get('project_pk')
        context['project'] = Project.objects.get(id=project_id)
        return context

    def list(self, request, *args, **kwargs):
        """获取项目成员列表"""
        project_id = self.kwargs.get('project_pk')

        # 检查项目是否存在
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # 添加项目创建者作为所有者
        owner_data = {
            'id': f'owner_{project.creator.id}',
            'user_id': project.creator.id,
            'username': project.creator.username,
            'email': project.creator.email,
            'role': 'owner',
            'joined_at': project.created_at,
            'is_owner': True
        }

        return Response([owner_data] + serializer.data)

    def create(self, request, *args, **kwargs):
        """添加项目成员"""
        project_id = self.kwargs.get('project_pk')

        # 检查项目是否存在
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 检查权限：只有项目创建者可以添加成员
        if project.creator != request.user:
            return Response({'error': '只有项目创建者可以添加成员'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectMemberCreateSerializer(
            data=request.data,
            context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)

        # 返回完整的成员信息
        member = ProjectMember.objects.get(
            project=project,
            user=serializer.validated_data['user']
        )
        response_serializer = ProjectMemberSerializer(member)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """移除项目成员"""
        project_id = self.kwargs.get('project_pk')

        # 检查项目是否存在
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 检查权限：只有项目创建者可以移除成员
        if project.creator != request.user:
            return Response({'error': '只有项目创建者可以移除成员'}, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """变更成员角色"""
        project_id = self.kwargs.get('project_pk')

        # 检查项目是否存在
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 检查权限：只有项目创建者可以变更成员角色
        if project.creator != request.user:
            return Response({'error': '只有项目创建者可以变更成员角色'}, status=status.HTTP_403_FORBIDDEN)

        member = self.get_object()
        serializer = ProjectMemberSerializer(
            member,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'creator']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 管理员和超级管理员可以看到所有项目
        if user.role in ['admin', 'super_admin']:
            return queryset

        # 其他用户可以看到：自己创建的项目 + 作为成员加入的项目
        from django.db.models import Q

        # 获取用户作为成员加入的项目ID列表
        member_project_ids = ProjectMember.objects.filter(
            user=user
        ).values_list('project_id', flat=True)

        # 筛选：创建者是用户 OR 用户是项目成员
        queryset = queryset.filter(
            Q(creator=user) | Q(id__in=member_project_ids)
        ).distinct()

        return queryset
