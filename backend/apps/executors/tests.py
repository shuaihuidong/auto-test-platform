"""
执行器模块单元测试
"""
from django.test import TestCase
from apps.executors.models import Executor, TaskQueue
from apps.users.models import User


class ExecutorModelTest(TestCase):
    """执行器模型测试"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_executor(self):
        """测试创建执行器"""
        executor = Executor.objects.create(
            name='测试执行器',
            uuid='test-uuid-123',
            status='online',
            max_concurrent=3,
            created_by=self.user
        )
        self.assertEqual(executor.name, '测试执行器')
        self.assertEqual(executor.status, 'online')
        self.assertEqual(executor.max_concurrent, 3)
        self.assertEqual(executor.created_by, self.user)

    def test_executor_str(self):
        """测试执行器字符串表示"""
        executor = Executor.objects.create(
            name='测试执行器',
            uuid='test-uuid-123',
            status='online',
            created_by=self.user
        )
        self.assertEqual(str(executor), '测试执行器')


class TaskQueueModelTest(TestCase):
    """任务队列模型测试"""

    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.executor = Executor.objects.create(
            name='测试执行器',
            uuid='test-uuid-123',
            status='online',
            created_by=self.user
        )

    def test_create_task(self):
        """测试创建任务"""
        task = TaskQueue.objects.create(
            script_data={'test': 'data'},
            status='pending',
            priority=1,
            assigned_executor=self.executor
        )
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.assigned_executor, self.executor)

    def test_task_default_priority(self):
        """测试任务默认优先级"""
        task = TaskQueue.objects.create(
            script_data={'test': 'data'},
            status='pending'
        )
        self.assertEqual(task.priority, 0)

    def test_task_str(self):
        """测试任务字符串表示"""
        task = TaskQueue.objects.create(
            script_data={'test': 'data'},
            status='pending'
        )
        self.assertIn('Task', str(task))
