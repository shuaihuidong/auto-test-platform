from rest_framework import permissions


class RolePermission(permissions.BasePermission):
    """
    基于角色的权限控制
    """

    # 角色等级映射 (数值越大权限越高)
    ROLE_LEVELS = {
        'guest': 1,
        'tester': 2,
        'admin': 3,
        'super_admin': 4,
    }

    # 各角色对应的权限
    ROLE_PERMISSIONS = {
        'guest': ['view', 'list'],
        'tester': ['view', 'list', 'create', 'execute'],
        'admin': ['view', 'list', 'create', 'update', 'delete', 'execute'],
        'super_admin': ['view', 'list', 'create', 'update', 'delete', 'execute', 'manage_users', 'manage_settings'],
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role = user.role
        if role not in self.ROLE_PERMISSIONS:
            return False

        # 获取请求方法对应的权限类型
        method_permissions = {
            'GET': 'view',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }

        # 列表视图使用 list 权限
        if hasattr(view, 'action') and view.action == 'list':
            required_perm = 'list'
        else:
            required_perm = method_permissions.get(request.method, 'view')

        return required_perm in self.ROLE_PERMISSIONS[role]

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsSuperAdmin(permissions.BasePermission):
    """仅超级管理员可访问"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'super_admin'


class IsAdmin(permissions.BasePermission):
    """管理员及以上可访问"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'super_admin']


class IsTester(permissions.BasePermission):
    """测试人员及以上可访问"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['tester', 'admin', 'super_admin']


class IsGuestOrAbove(permissions.BasePermission):
    """访客及以上（所有登录用户）可访问"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
