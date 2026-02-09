from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Plan
from .serializers import PlanSerializer


class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """获取查询集 - 只返回当前用户创建的项目中的计划"""
        from django.db.models import Q
        user = self.request.user

        # 管理员和超级管理员可以看到所有计划
        if user.role in ['admin', 'super_admin']:
            return Plan.objects.select_related('project', 'created_by').all()

        # 其他用户只能看到自己创建的项目的计划
        user_created_projects = user.created_projects.all()
        return Plan.objects.select_related('project', 'created_by').filter(
            Q(project__in=user_created_projects) | Q(created_by=user)
        ).distinct()

    @action(detail=True, methods=['post'])
    def add_script(self, request, pk=None):
        """向计划添加脚本"""
        plan = self.get_object()
        script_id = request.data.get('script_id')
        if not script_id:
            return Response({'error': '请提供script_id'}, status=400)

        if plan.script_ids is None:
            plan.script_ids = []
        if script_id not in plan.script_ids:
            plan.script_ids.append(script_id)
            plan.save()
        return Response({'message': '添加成功', 'script_ids': plan.script_ids})

    @action(detail=True, methods=['post'])
    def remove_script(self, request, pk=None):
        """从计划移除脚本"""
        plan = self.get_object()
        script_id = request.data.get('script_id')
        if not script_id:
            return Response({'error': '请提供script_id'}, status=400)

        if plan.script_ids and script_id in plan.script_ids:
            plan.script_ids.remove(script_id)
            plan.save()
        return Response({'message': '移除成功', 'script_ids': plan.script_ids})
