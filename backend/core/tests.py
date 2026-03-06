"""
中间件单元测试
"""
from django.test import TestCase, RequestFactory
from core.middleware import DisableCSRFMiddleware


class DisableCSRFMiddlewareTest(TestCase):
    """CSRF中间件测试"""

    def setUp(self):
        """设置测试数据"""
        self.factory = RequestFactory()
        self.middleware = DisableCSRFMiddleware(lambda x: x)

    def test_exempt_login_path(self):
        """测试登录路径豁免CSRF"""
        request = self.factory.post('/api/auth/login/')
        self.middleware(request)
        self.assertTrue(getattr(request, '_dont_enforce_csrf_checks', False))

    def test_exempt_logout_path(self):
        """测试登出路径豁免CSRF"""
        request = self.factory.post('/api/auth/logout/')
        self.middleware(request)
        self.assertTrue(getattr(request, '_dont_enforce_csrf_checks', False))

    def test_exempt_executor_register_path(self):
        """测试执行器注册路径豁免CSRF"""
        request = self.factory.post('/api/executor/register/')
        self.middleware(request)
        self.assertTrue(getattr(request, '_dont_enforce_csrf_checks', False))

    def test_exempt_executor_heartbeat_path(self):
        """测试执行器心跳路径豁免CSRF"""
        request = self.factory.post('/api/executor/heartbeat/')
        self.middleware(request)
        self.assertTrue(getattr(request, '_dont_enforce_csrf_checks', False))

    def test_non_exempt_path(self):
        """测试非豁免路径不豁免CSRF"""
        request = self.factory.post('/api/users/')
        self.middleware(request)
        self.assertFalse(getattr(request, '_dont_enforce_csrf_checks', False))

    def test_exempt_exact_path_only(self):
        """测试只有精确匹配才豁免"""
        # 不应该豁免的路径
        paths_not_exempt = [
            '/api/auth/login/test/',
            '/api/auth/login',
            '/api/users/login/',
        ]
        for path in paths_not_exempt:
            request = self.factory.post(path)
            self.middleware(request)
            self.assertFalse(
                getattr(request, '_dont_enforce_csrf_checks', False),
                f'路径 {path} 不应该被豁免'
            )
