from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    LoginSerializer,
    ChangePasswordSerializer
)
from .permissions import IsSuperAdmin, IsAdmin, IsTester, IsGuestOrAbove

User = get_user_model()


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """登录视图 - 豁免 CSRF"""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        # 生成token用于WebSocket认证（使用session key作为token）
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        import secrets

        # 为执行机客户端生成一个简单的token
        # 实际生产环境应该使用更安全的token生成方式
        token = secrets.token_hex(32)

        # 将token存储在session中供WebSocket验证使用
        request.session['executor_token'] = token
        request.session['executor_user_id'] = user.id
        request.session.save()

        return Response({
            'message': '登录成功',
            'token': token,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': '用户名或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsGuestOrAbove]

    def get_permissions(self):
        """根据不同操作应用不同权限"""
        if self.action in ['create', 'destroy', 'set_role']:
            # 创建/删除用户和修改角色：仅管理员
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update']:
            # 更新用户信息：管理员
            return [IsAdmin()]
        elif self.action == 'list':
            # 列表：测试人员及以上
            return [IsTester()]
        return [IsGuestOrAbove()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': '登出成功'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def permissions(self, request):
        """获取当前用户的权限列表"""
        from .permissions import RolePermission
        role_perms = RolePermission.ROLE_PERMISSIONS.get(request.user.role, [])
        return Response({
            'role': request.user.role,
            'role_display': request.user.get_role_display(),
            'permissions': role_perms
        })

    @action(detail=True, methods=['post'])
    def set_role(self, request, pk=None):
        """设置用户角色 - 仅超级管理员"""
        if request.user.role != 'super_admin':
            return Response(
                {'error': '只有超级管理员可以修改用户角色'},
                status=status.HTTP_403_FORBIDDEN
            )
        user = self.get_object()
        new_role = request.data.get('role')
        valid_roles = ['super_admin', 'admin', 'tester', 'guest']
        if new_role not in valid_roles:
            return Response(
                {'error': '无效的角色'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.role = new_role
        user.save()
        return Response({
            'message': f'用户角色已更新为 {user.get_role_display()}',
            'user': UserSerializer(user).data
        })

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码 - 仅管理员"""
        # 检查权限
        if request.user.role not in ['admin', 'super_admin']:
            return Response(
                {'error': '只有管理员可以重置用户密码'},
                status=status.HTTP_403_FORBIDDEN
            )

        user = self.get_object()

        # 不能重置自己的密码
        if user.id == request.user.id:
            return Response(
                {'error': '不能重置自己的密码，请使用修改密码功能'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 重置为默认密码
        default_password = '123456'
        user.set_password(default_password)
        user.save()

        return Response({
            'message': f'用户 {user.username} 的密码已重置为默认密码',
            'default_password': default_password,
            'user': UserSerializer(user).data
        })

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码 - 所有登录用户"""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response(
                {'error': '原密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({'message': '密码修改成功'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_rabbitmq_user(self, request):
        """创建 RabbitMQ 用户 - 仅超级管理员"""
        # 检查权限：只有超级管理员可以创建 RabbitMQ 用户
        if request.user.role != 'super_admin':
            return Response(
                {'error': '只有超级管理员可以创建 RabbitMQ 用户'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username')
        password = request.data.get('password')
        tags = request.data.get('tags', 'management')

        if not username or not password:
            return Response(
                {'error': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            import requests
            from django.conf import settings

            # 使用 RabbitMQ HTTP API 创建用户
            rabbitmq_api_url = f"http://{settings.RABBITMQ_HOST}:15672/api/users/{username}"
            auth = (settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)

            # 创建用户
            response = requests.put(
                rabbitmq_api_url,
                json={
                    "password": password,
                    "tags": tags
                },
                auth=auth
            )

            if response.status_code in [200, 201]:
                # 设置用户权限（对虚拟主机 / 的完全权限）
                permissions_url = f"http://{settings.RABBITMQ_HOST}:15672/api/permissions/%2F/{username}"
                permissions_response = requests.put(
                    permissions_url,
                    json={
                        "configure": ".*",
                        "write": ".*",
                        "read": ".*"
                    },
                    auth=auth
                )

                if permissions_response.status_code in [200, 201]:
                    return Response({
                        'message': f'RabbitMQ 用户 {username} 创建成功',
                        'username': username,
                        'password': password,
                        'tags': tags,
                        'note': '请将该信息提供给执行机用户，用于配置执行机客户端'
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {'error': f'用户创建成功但设置权限失败: {permissions_response.text}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(
                    {'error': f'创建用户失败: {response.text}'},
                    status=response.status_code
                )

        except requests.exceptions.ConnectionError:
            return Response(
                {'error': '无法连接到 RabbitMQ 管理接口，请确认 RabbitMQ 服务已启动'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': f'创建用户时发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def list_rabbitmq_users(self, request):
        """列出 RabbitMQ 用户 - 仅超级管理员"""
        if request.user.role != 'super_admin':
            return Response(
                {'error': '只有超级管理员可以查看 RabbitMQ 用户'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            import requests
            from django.conf import settings

            # 获取用户列表
            users_url = f"http://{settings.RABBITMQ_HOST}:15672/api/users/"
            auth = (settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)

            response = requests.get(users_url, auth=auth)

            if response.status_code == 200:
                users_data = response.json()
                # 过滤掉系统内置用户（guest 通常在系统中有特殊用途）
                users_list = []
                for user_info in users_data:
                    # 跳过 guest 用户（系统默认，只允许本地访问）
                    if user_info.get('name') != 'guest':
                        users_list.append({
                            'name': user_info.get('name'),
                            'tags': user_info.get('tags', ''),
                            'hashing_algorithm': user_info.get('hashing_algorithm', ''),
                        })
                return Response({'users': users_list})
            else:
                return Response(
                    {'error': f'获取用户列表失败: {response.text}'},
                    status=response.status_code
                )

        except requests.exceptions.ConnectionError:
            return Response(
                {'error': '无法连接到 RabbitMQ 管理接口'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': f'获取用户列表时发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post', 'delete'])
    def delete_rabbitmq_user(self, request):
        """删除 RabbitMQ 用户 - 仅超级管理员"""
        if request.user.role != 'super_admin':
            return Response(
                {'error': '只有超级管理员可以删除 RabbitMQ 用户'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username') if request.method == 'POST' else request.query_params.get('username')

        if not username:
            return Response(
                {'error': '请提供要删除的用户名'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 不允许删除 guest 用户
        if username == 'guest':
            return Response(
                {'error': '不能删除 guest 系统用户'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            import requests
            from django.conf import settings

            # 删除用户
            user_url = f"http://{settings.RABBITMQ_HOST}:15672/api/users/{username}"
            auth = (settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)

            response = requests.delete(user_url, auth=auth)

            if response.status_code in [200, 204]:
                return Response({'message': f'RabbitMQ 用户 {username} 已删除'})
            else:
                return Response(
                    {'error': f'删除用户失败: {response.text}'},
                    status=response.status_code
                )

        except requests.exceptions.ConnectionError:
            return Response(
                {'error': '无法连接到 RabbitMQ 管理接口'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': f'删除用户时发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def update_rabbitmq_user_password(self, request):
        """修改 RabbitMQ 用户密码 - 仅超级管理员"""
        if request.user.role != 'super_admin':
            return Response(
                {'error': '只有超级管理员可以修改 RabbitMQ 用户密码'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username')
        new_password = request.data.get('password')

        if not username or not new_password:
            return Response(
                {'error': '用户名和新密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            import requests
            from django.conf import settings

            # 修改用户密码
            user_url = f"http://{settings.RABBITMQ_HOST}:15672/api/users/{username}"
            auth = (settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)

            response = requests.put(
                user_url,
                json={"password": new_password},
                auth=auth
            )

            if response.status_code in [200, 201]:
                return Response({
                    'message': f'RabbitMQ 用户 {username} 密码已修改',
                    'username': username,
                    'password': new_password
                })
            else:
                return Response(
                    {'error': f'修改密码失败: {response.text}'},
                    status=response.status_code
                )

        except requests.exceptions.ConnectionError:
            return Response(
                {'error': '无法连接到 RabbitMQ 管理接口'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': f'修改密码时发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_list(request):
    """获取角色列表 - 管理员及以上"""
    if request.user.role not in ['admin', 'super_admin']:
        return Response(
            {'error': '无权限访问'},
            status=status.HTTP_403_FORBIDDEN
        )

    from .permissions import RolePermission
    from .models import User

    roles = []
    for role_value, role_label in User.ROLE_CHOICES:
        # 统计每个角色的用户数量
        count = User.objects.filter(role=role_value).count()
        roles.append({
            'value': role_value,
            'label': role_label,
            'level': RolePermission.ROLE_LEVELS.get(role_value, 0),
            'permissions': RolePermission.ROLE_PERMISSIONS.get(role_value, []),
            'user_count': count
        })

    return Response({'results': roles})


@api_view(['GET', 'PUT'])
@permission_classes([IsSuperAdmin])
def role_detail(request, role):
    """获取或更新角色详情 - 仅超级管理员"""
    from .permissions import RolePermission
    from .models import User

    # 验证角色是否存在
    valid_roles = [r[0] for r in User.ROLE_CHOICES]
    if role not in valid_roles:
        return Response(
            {'error': '角色不存在'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        # 获取角色详情
        role_label = dict(User.ROLE_CHOICES).get(role, role)
        users = User.objects.filter(role=role)
        user_data = UserSerializer(users, many=True).data

        return Response({
            'value': role,
            'label': role_label,
            'level': RolePermission.ROLE_LEVELS.get(role, 0),
            'permissions': RolePermission.ROLE_PERMISSIONS.get(role, []),
            'users': user_data,
            'user_count': users.count()
        })

    elif request.method == 'PUT':
        # 更新角色权限（超级管理员功能）
        new_permissions = request.data.get('permissions', [])
        valid_permissions = ['view', 'list', 'create', 'update', 'delete', 'execute', 'manage_users', 'manage_settings']

        # 验证权限
        for perm in new_permissions:
            if perm not in valid_permissions:
                return Response(
                    {'error': f'无效的权限: {perm}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 注意：这里只是示例，实际权限应该存储在数据库中
        # 当前权限是硬编码在 permissions.py 中的
        # 如果要支持动态修改权限，需要创建 Role 模型来存储

        return Response(
            {'error': '当前权限系统为硬编码，不支持动态修改。如需修改，请编辑 permissions.py 文件'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_users(request, role):
    """获取指定角色的用户列表 - 管理员及以上"""
    if request.user.role not in ['admin', 'super_admin']:
        return Response(
            {'error': '无权限访问'},
            status=status.HTTP_403_FORBIDDEN
        )

    from .models import User

    # 验证角色是否存在
    valid_roles = [r[0] for r in User.ROLE_CHOICES]
    if role not in valid_roles:
        return Response(
            {'error': '角色不存在'},
            status=status.HTTP_404_NOT_FOUND
        )

    users = User.objects.filter(role=role)
    serializer = UserSerializer(users, many=True)

    return Response({
        'role': role,
        'role_label': dict(User.ROLE_CHOICES).get(role, role),
        'users': serializer.data,
        'count': users.count()
    })
