"""
Task Distributor Service

自动任务分发服务 - 负责将待分配的任务自动分发给可用的执行机
"""
import logging
from typing import Optional
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.executors.models import Executor, TaskQueue
from apps.executions.models import Execution

logger = logging.getLogger(__name__)


class TaskDistributor:
    """
    任务分发服务

    功能:
    - 扫描待分配的任务
    - 自动选择合适的执行机
    - 分配任务并通过 WebSocket 下发
    """

    def distribute_tasks(self, limit: int = 50) -> int:
        """
        分发待分配的任务

        Args:
            limit: 最多分发的任务数

        Returns:
            成功分发的任务数
        """
        distributed_count = 0

        # 获取待分配的任务（按优先级排序）
        pending_tasks = TaskQueue.objects.filter(
            status='pending'
        ).order_by(
            '-priority',  # 优先级高的先分配
            'created_at'  # 创建时间早的先分配
        )[:limit]

        logger.info(f"开始分发任务，共 {len(pending_tasks)} 个待分配任务")

        for task in pending_tasks:
            try:
                logger.info(f"正在处理任务 {task.id}, execution_id={task.execution_id}, status={task.status}")
                # 获取执行模式
                execution_mode = task.script_data.get('execution_mode', 'parallel')
                parent_execution_id = task.script_data.get('parent_execution_id')

                # 如果是顺序执行，检查前一个脚本是否已完成
                if execution_mode == 'sequential' and parent_execution_id:
                    script_index = task.script_data.get('script_index', 0)

                    # 如果不是第一个脚本(script_index > 0)，需要检查前一个脚本是否完成
                    if script_index > 0:
                        # 使用 select_for_update 锁定行
                        with transaction.atomic():
                            # 重新查询最新的任务状态
                            task = TaskQueue.objects.select_for_update().get(id=task.id)
                            if task.status != 'pending':
                                continue

                            # 检查前一个脚本的执行状态（通过 parent_id 和 id 排序来确定顺序）
                            # 由于 script_index 是按创建顺序分配的，可以通过查询 parent_id 相同且 id 小于当前 execution_id 的执行数量来验证
                            # 更直接的方式：查询所有同父执行的子任务，按 id 排序，检查 script_index-1 的状态

                            # 获取当前 execution 对象
                            try:
                                current_execution = Execution.objects.get(id=task.execution_id)
                            except Execution.DoesNotExist:
                                logger.warning(f"找不到执行记录 {task.execution_id}，跳过任务 {task.id}")
                                continue

                            # 查询同父执行的所有子任务，按 id 排序
                            sibling_executions = Execution.objects.filter(
                                parent_id=parent_execution_id
                            ).order_by('id')

                            # 检查前一个脚本是否已完成
                            if script_index <= len(sibling_executions):
                                prev_execution = sibling_executions[script_index - 1]

                                # 如果前一个脚本未完成，跳过当前任务
                                if prev_execution.status not in ['completed', 'failed', 'stopped']:
                                    logger.info(f"任务 {task.id} (执行ID: {task.execution_id}, 脚本索引: {script_index}) "
                                              f"等待前一个脚本 (执行ID: {prev_execution.id}, 状态: {prev_execution.status}) 完成")
                                    continue  # 跳过此任务，等待下次分发

                executor = self._find_available_executor(task)
                if executor:
                    self._assign_task(task, executor)
                    distributed_count += 1
                    logger.info(f"任务 {task.id} (执行ID: {task.execution_id}) 已分配给执行机 {executor.name}")
                else:
                    logger.warning(f"没有可用的执行机处理任务 {task.id}")
            except Exception as e:
                logger.error(f"分发任务 {task.id} 失败: {str(e)}", exc_info=True)

        logger.info(f"任务分发完成，成功分发 {distributed_count} 个任务")
        return distributed_count

    def _find_available_executor(self, task: TaskQueue) -> Optional[Executor]:
        """
        查找可用的执行机

        选择策略:
        1. 在线 + 启用
        2. 优先匹配项目专用执行机
        3. 其次使用全局可用执行机
        4. 考虑当前任务数，选择负载最低的（作为参考，不强制限制）

        注意：并发控制由执行机端负责
        - 执行机检查 current_tasks < max_concurrent
        - 达到限制时拒绝任务（NACK + requeue=True）
        - 后端重新分发被拒绝的任务

        Args:
            task: 待分配的任务

        Returns:
            可用的执行机，如果没有则返回 None
        """
        # 获取脚本所属项目
        project = None
        if task.execution and task.execution.script:
            project = task.execution.script.project

        # 基础查询条件: 在线 + 启用
        # 不再检查并发上限，由执行机端自己控制
        base_queryset = Executor.objects.filter(
            is_enabled=True,
            status__in=['idle', 'online', 'busy'],  # 包含所有在线状态
            last_heartbeat__gte=timezone.now() - timezone.timedelta(seconds=120)
        )

        # 优先查找项目专用执行机
        if project:
            # 作为参考，按当前任务数排序（不强制限制）
            project_executors = base_queryset.filter(
                scope='project',
                bound_projects=project
            ).annotate(
                running_count=models.Count(
                    'tasks',
                    filter=models.Q(tasks__status='running')
                )
            ).order_by('running_count')  # 优先选择负载低的

            if project_executors.exists():
                return project_executors.first()

        # 查找全局可用执行机
        global_executors = base_queryset.filter(
            scope='global'
        ).annotate(
            running_count=models.Count(
                'tasks',
                filter=models.Q(tasks__status='running')
            )
        ).order_by('running_count')  # 优先选择负载低的

        if global_executors.exists():
            return global_executors.first()

        return None

    def _assign_task(self, task: TaskQueue, executor: Executor) -> None:
        """
        分配任务给执行机

        Args:
            task: 待分配的任务
            executor: 目标执行机
        """
        with transaction.atomic():
            # 更新任务状态
            task.executor = executor
            task.status = 'assigned'
            task.assigned_at = timezone.now()
            task.save()

            # 更新执行机当前任务数
            executor.current_tasks += 1
            executor.save()

        # 通过消息队列发送任务到执行机
        self._send_task_to_executor(task, executor)

    def _send_task_to_executor(self, task: TaskQueue, executor: Executor) -> None:
        """
        通过消息队列发送任务到执行机

        Args:
            task: 任务对象
            executor: 执行机对象
        """
        from services.message_queue import get_message_queue_publisher

        # 准备任务数据
        task_data = {
            'task_id': task.id,
            'execution_id': task.execution_id,
            'script_data': task.script_data,
            'browser_type': task.script_data.get('browser_type', 'chrome'),
            'timeout': task.script_data.get('timeout', 300),
            'variables': self._get_execution_variables(task.execution)
        }

        # 通过消息队列发送到执行机
        try:
            publisher = get_message_queue_publisher()
            success = publisher.publish_task(str(executor.uuid), task_data)

            if success:
                logger.info(f"任务 {task.id} 已通过消息队列发送到执行机 {executor.name}")
            else:
                # 发送失败，回退任务状态
                task.status = 'pending'
                task.executor = None
                task.assigned_at = None
                task.save()

                # 回退执行机任务数
                executor.current_tasks = max(0, executor.current_tasks - 1)
                executor.save()

        except Exception as e:
            logger.error(f"发送任务到执行机失败: {str(e)}")
            # 发送失败，回退任务状态
            task.status = 'pending'
            task.executor = None
            task.assigned_at = None
            task.save()

            # 回退执行机任务数
            executor.current_tasks = max(0, executor.current_tasks - 1)
            executor.save()

    def _get_execution_variables(self, execution: Execution) -> dict:
        """
        获取执行所需的变量

        Args:
            execution: 执行对象

        Returns:
            变量字典
        """
        variables = {}

        # 获取项目级变量
        if execution.script and execution.script.project:
            from apps.executors.models import Variable
            project_vars = Variable.objects.filter(
                scope='project',
                project=execution.script.project
            )
            for var in project_vars:
                variables[var.name] = var.value

        # 获取脚本级变量（会覆盖项目级变量）
        if execution.script:
            from apps.executors.models import Variable
            script_vars = Variable.objects.filter(
                scope='script',
                script=execution.script
            )
            for var in script_vars:
                variables[var.name] = var.value

        return variables

    def redistribute_task(self, task_id: int) -> bool:
        """
        重新分配任务（用于执行机故障时）

        Args:
            task_id: 任务ID

        Returns:
            是否成功重新分配
        """
        try:
            task = TaskQueue.objects.get(id=task_id)

            if task.status not in ['assigned', 'running']:
                logger.warning(f"任务 {task_id} 状态为 {task.status}，不需要重新分配")
                return False

            # 释放原执行机
            if task.executor:
                task.executor.current_tasks = max(0, task.executor.current_tasks - 1)
                task.executor.save()

            # 重置任务状态
            task.status = 'pending'
            task.executor = None
            task.assigned_at = None
            task.save()

            # 重新分发
            executor = self._find_available_executor(task)
            if executor:
                self._assign_task(task, executor)
                logger.info(f"任务 {task_id} 已重新分配给执行机 {executor.name}")
                return True
            else:
                logger.warning(f"没有可用的执行机重新分配任务 {task_id}")
                return False

        except TaskQueue.DoesNotExist:
            logger.error(f"任务 {task_id} 不存在")
            return False
        except Exception as e:
            logger.error(f"重新分配任务 {task_id} 失败: {str(e)}")
            return False

    def cancel_pending_tasks(self, execution_id: int) -> int:
        """
        取消某个执行的所有待分配任务

        Args:
            execution_id: 执行ID

        Returns:
            取消的任务数
        """
        count = TaskQueue.objects.filter(
            execution_id=execution_id,
            status='pending'
        ).update(
            status='cancelled'
        )
        logger.info(f"已取消执行 {execution_id} 的 {count} 个待分配任务")
        return count
