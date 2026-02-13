from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectMemberViewSet

router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

# 项目成员管理路由
members_router = DefaultRouter()
members_router.register(
    r'(?P<project_pk>\d+)/members',
    ProjectMemberViewSet,
    basename='project-members'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(members_router.urls)),
]
