from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ScriptViewSet, basename='script')
router.register(r'datasources', views.DataSourceViewSet, basename='datasource')

urlpatterns = [
    # 自定义 action 路由
    path('modules/', views.ScriptViewSet.as_view({'get': 'modules'}), name='script-modules'),
] + router.urls
