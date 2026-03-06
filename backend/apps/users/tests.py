"""
用户模块单元测试
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.users.views import encrypt_rabbitmq_password, decrypt_rabbitmq_password

User = get_user_model()


class UserModelTest(TestCase):
    """用户模型测试"""

    def test_create_user(self):
        """测试创建用户"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'guest')  # 默认角色
        self.assertTrue(user.check_password('testpass123'))

    def test_create_superuser(self):
        """测试创建超级用户"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.assertEqual(user.role, 'super_admin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_str(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'testuser')


class PasswordEncryptionTest(TestCase):
    """密码加密测试"""

    def test_encrypt_decrypt_password(self):
        """测试密码加密和解密"""
        original_password = 'my-secret-password-123'

        # 加密
        encrypted = encrypt_rabbitmq_password(original_password)
        self.assertNotEqual(encrypted, original_password)
        self.assertGreater(len(encrypted), len(original_password))

        # 解密
        decrypted = decrypt_rabbitmq_password(encrypted)
        self.assertEqual(decrypted, original_password)

    def test_encrypt_different_passwords(self):
        """测试不同密码的加密结果不同"""
        password1 = 'password1'
        password2 = 'password2'

        encrypted1 = encrypt_rabbitmq_password(password1)
        encrypted2 = encrypt_rabbitmq_password(password2)

        self.assertNotEqual(encrypted1, encrypted2)

    def test_encrypt_same_password_twice(self):
        """测试相同密码加密两次结果不同（因为Fernet包含时间戳）"""
        password = 'same-password'

        encrypted1 = encrypt_rabbitmq_password(password)
        encrypted2 = encrypt_rabbitmq_password(password)

        # Fernet加密包含时间戳，所以两次加密结果不同
        self.assertNotEqual(encrypted1, encrypted2)

        # 但解密后应该相同
        self.assertEqual(decrypt_rabbitmq_password(encrypted1), password)
        self.assertEqual(decrypt_rabbitmq_password(encrypted2), password)


class UserRoleTest(TestCase):
    """用户角色测试"""

    def setUp(self):
        """设置测试数据"""
        self.super_admin = User.objects.create_user(
            username='superadmin',
            email='super@example.com',
            password='pass123',
            role='super_admin'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='pass123',
            role='admin'
        )
        self.tester = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='pass123',
            role='tester'
        )
        self.guest = User.objects.create_user(
            username='guest',
            email='guest@example.com',
            password='pass123',
            role='guest'
        )

    def test_role_choices(self):
        """测试角色选择"""
        self.assertEqual(self.super_admin.role, 'super_admin')
        self.assertEqual(self.admin.role, 'admin')
        self.assertEqual(self.tester.role, 'tester')
        self.assertEqual(self.guest.role, 'guest')

    def test_role_hierarchy(self):
        """测试角色层级（通过代码逻辑验证）"""
        # 这里可以添加权限检查逻辑
        roles = ['guest', 'tester', 'admin', 'super_admin']
        self.assertIn(self.guest.role, roles)
        self.assertIn(self.tester.role, roles)
        self.assertIn(self.admin.role, roles)
        self.assertIn(self.super_admin.role, roles)
