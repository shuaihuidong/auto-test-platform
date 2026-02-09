from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExecutorViewSet, ExecutorGroupViewSet, ExecutorTagViewSet,
    VariableViewSet, TaskQueueViewSet
)
from . import heartbeat

# 创建执行机路由
executor_router = DefaultRouter()
executor_router.register(r'', ExecutorViewSet, basename='executor')

# 创建执行机组路由
group_router = DefaultRouter()
group_router.register(r'', ExecutorGroupViewSet, basename='executor-group')

# 创建执行机标签路由
tag_router = DefaultRouter()
tag_router.register(r'', ExecutorTagViewSet, basename='executor-tag')

# 创建变量路由
variable_router = DefaultRouter()
variable_router.register(r'', VariableViewSet, basename='variable')

# 创建任务路由
task_router = DefaultRouter()
task_router.register(r'', TaskQueueViewSet, basename='task')

urlpatterns = [
    path('executors/', include(executor_router.urls)),
    path('executor-groups/', include(group_router.urls)),
    path('executor-tags/', include(tag_router.urls)),
    path('variables/', include(variable_router.urls)),
    path('tasks/', include(task_router.urls)),
    # 心跳和注册 API
    path('executor/heartbeat/', heartbeat.heartbeat_report, name='executor-heartbeat'),
    path('executor/register/', heartbeat.executor_register, name='executor-register'),
]
