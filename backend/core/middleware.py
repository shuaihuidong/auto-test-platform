class DisableCSRFMiddleware:
    """
    CSRF保护中间件 - 仅豁免特定API端点

    策略：
    - 登录/注册端点豁免CSRF（因为此时用户还未认证）
    - 执行器心跳/注册端点豁免（外部系统调用）
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
        # 仅豁免特定路径
        if request.path in self.EXEMPT_PATHS:
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)
