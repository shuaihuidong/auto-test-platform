from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, login_view, role_list, role_detail, role_users

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('login/', login_view),
    # 角色管理 API - 必须放在 router.urls 之前
    path('roles/', role_list),
    path('roles/<str:role>/', role_detail),
    path('roles/<str:role>/users/', role_users),
    path('', include(router.urls)),
]
