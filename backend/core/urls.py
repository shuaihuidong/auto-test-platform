"""
URL configuration for auto test platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/scripts/', include('apps.scripts.urls')),
    path('api/plans/', include('apps.plans.urls')),
    path('api/executions/', include('apps.executions.urls')),
    # executors app 包含所有相关路由
    path('api/', include('apps.executors.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/drivers/', include('apps.drivers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
