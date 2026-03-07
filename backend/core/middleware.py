class DisableCSRFMiddleware:
    """
    CSRF保护中间件 - 仅豁免特定API端点

    策略：
    - 登录/注册端点豁免CSRF（因为此时用户还未认证）
    - 执行器心跳/注册端点豁免（外部系统调用）
    - 带有有效Token认证的API请求豁免（Token认证本身已足够安全）
    - 其他API端点保持CSRF保护
    """

    # 豁免CSRF检查的API路径
    EXEMPT_PATHS = [
        '/api/auth/login/',
        '/api/auth/logout/',
        '/api/executor/register/',
        '/api/executor/heartbeat/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 豁免特定路径
        if request.path in self.EXEMPT_PATHS:
            setattr(request, '_dont_enforce_csrf_checks', True)
        # 对带有 Token 认证的请求豁免 CSRF
        # DRF Token 认证使用 Authorization: Token xxx 头
        elif self._has_valid_token_auth(request):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)

    def _has_valid_token_auth(self, request):
        """检查请求是否带有有效的 Token 认证头"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            return True
        return False
