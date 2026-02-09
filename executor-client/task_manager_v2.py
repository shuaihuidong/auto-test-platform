"""
任务管理器 V2 - 集成消息队列和 HTTP 心跳

主要变更:
1. 使用 RabbitMQ 消息队列接收任务，替代 WebSocket
2. 使用 HTTP API 上报心跳和状态
3. 保留 WebSocket 仅用于 Web UI 状态展示（可选）
"""

import threading
import time
import traceback
from typing import Dict, Any, Optional
from loguru import logger
import requests

from config import get_config_manager, ExecutorConfig
from executor import ScriptExecutor
from message_queue_client import get_message_queue_consumer
from utils.system import get_resource_usage

# 添加文件日志（用于调试）
logger.add(
    "debug_executor.log",
    rotation="10 MB",
    retention="3 days",
    level="DEBUG",
    enqueue=True
)


class TaskManagerV2:
    """
    任务管理器 V2

    负责：
    1. 从消息队列接收任务并执行
    2. 通过 HTTP 上报心跳和状态
    3. 实时上报日志和截图到平台
    """

    def __init__(self):
        self.config: ExecutorConfig = get_config_manager().get()
        self.mq_consumer = get_message_queue_consumer()
        self.running_tasks: Dict[str, Dict[str, Any]] = {}  # task_id -> task_info
        self.cancelled_tasks: set = set()

        # 保存计划执行信息（用于GUI显示），任务完成后不删除
        self.plan_executions: Dict[str, Dict[str, Any]] = {}  # parent_execution_id -> plan_info

        # 心跳线程
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._is_heartbeat_running = False

        # 任务完成回调
        self.on_task_complete = None  # callable(task_id, status, message)

        # 顺序执行的等待队列：parent_execution_id -> [等待的任务列表]
        self._sequential_wait_queue: Dict[str, list] = {}
        self._wait_lock = threading.Lock()

        # 设置消息队列回调
        self.mq_consumer.on_task_received = self.on_task_received
        self.mq_consumer.on_connected = self.on_mq_connected
        self.mq_consumer.on_disconnected = self.on_mq_disconnected
        self.mq_consumer.on_error = self.on_mq_error

    def connect(self) -> bool:
        """
        连接到服务器（注册执行机 + 启动消息队列消费者 + 启动心跳）

        Returns:
            是否连接成功
        """
        try:
            # 1. 注册执行机
            if not self._register_executor():
                return False

            # 2. 启动消息队列消费者
            if not self.mq_consumer.start():
                logger.error("启动消息队列消费者失败")
                return False

            # 3. 启动心跳线程
            self._start_heartbeat()

            logger.info("执行机已成功连接到平台")
            return True

        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False

    def _register_executor(self, max_retries: int = 5, initial_delay: float = 2.0) -> bool:
        """
        注册执行机到平台（带重试机制）

        Args:
            max_retries: 最大重试次数（默认5次）
            initial_delay: 初始重试延迟秒数（默认2秒）

        Returns:
            是否注册成功
        """
        import time

        api_base = self.config.server_url.rstrip('/')
        register_url = f"{api_base}/api/executor/register/"

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    register_url,
                    json={
                        "executor_uuid": self.config.executor_uuid,
                        "executor_name": self.config.executor_name,
                        "platform": "Windows",
                        "browser_types": ["chrome", "firefox", "edge"],
                        "owner_username": self.config.owner_username
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    logger.info("执行机注册成功")
                    return True
                else:
                    logger.warning(f"执行机注册失败: HTTP {response.status_code}")

            except Exception as e:
                logger.warning(f"执行机注册异常 (尝试 {attempt + 1}/{max_retries}): {e}")

            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)  # 指数退避
                logger.info(f"等待 {delay:.1f} 秒后重试注册...")
                time.sleep(delay)
            else:
                logger.error(f"执行机注册失败：已达到最大重试次数 ({max_retries})")

        return False

    def _start_heartbeat(self):
        """启动心跳线程"""
        if self._is_heartbeat_running:
            return

        self._is_heartbeat_running = True
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,
            name="Heartbeat"
        )
        self._heartbeat_thread.start()
        logger.info("心跳线程已启动")

    def _heartbeat_loop(self):
        """心跳循环（在单独线程中运行）"""
        import time

        while self._is_heartbeat_running:
            try:
                # 上报心跳
                self._send_heartbeat()

                # 等待下次心跳
                time.sleep(self.config.heartbeat_interval)

            except Exception as e:
                logger.error(f"心跳发送失败: {e}")
                time.sleep(5)  # 出错后短暂等待

    def _send_heartbeat(self):
        """发送心跳"""
        try:
            # 获取系统资源使用情况
            resources = get_resource_usage()
            current_tasks = len(self.running_tasks)

            # 确定状态
            if current_tasks == 0:
                status = "idle"
            elif current_tasks < self.config.max_concurrent:
                status = "busy"
            else:
                status = "busy"

            # 构建 API URL
            api_base = self.config.server_url.rstrip('/')
            heartbeat_url = f"{api_base}/api/executor/heartbeat/"

            response = requests.post(
                heartbeat_url,
                json={
                    "executor_uuid": self.config.executor_uuid,
                    "status": status,
                    "current_tasks": current_tasks,
                    "cpu_usage": resources.get("cpu", 0),
                    "memory_usage": resources.get("memory", 0),
                    "disk_usage": resources.get("disk", 0),
                    "message": ""
                },
                timeout=5
            )

            if response.status_code == 200:
                logger.debug(f"心跳上报成功: status={status}, tasks={current_tasks}")
            else:
                logger.warning(f"心跳上报失败: HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"心跳上报异常: {e}")

    def on_task_received(self, task_data: Dict[str, Any]) -> bool:
        """
        收到任务时的回调（在消息队列线程中调用）

        Args:
            task_data: 任务数据

        Returns:
            任务是否成功接收（返回 False 会拒绝任务，让 RabbitMQ 重新排队）
        """
        task_id = task_data.get("task_id", "")
        script_data = task_data.get("script_data", {})
        script_name = script_data.get("name", "未命名脚本")
        execution_mode = script_data.get("execution_mode", "parallel")
        parent_execution_id = script_data.get("parent_execution_id")
        plan_scripts = script_data.get("plan_scripts", [])

        # 【关键修复】先加入 running_tasks，再检查并发限制
        # 这样可以避免竞态条件：多个任务同时到达时都能看到对方的占用
        execution_id = task_data.get("execution_id")
        self.running_tasks[task_id] = {
            "execution_id": execution_id,
            "script_name": script_name,
            "status": "starting",  # 初始状态为 starting
        }

        # 现在检查并发限制
        current_tasks = len(self.running_tasks)
        if current_tasks > self.config.max_concurrent:
            # 超过限制，从 running_tasks 中移除并拒绝任务
            del self.running_tasks[task_id]
            logger.warning(f"执行机已达到最大并发数 ({self.config.max_concurrent})，拒绝接收新任务 {task_id}")
            return False  # 返回 False 拒绝任务，消息会重新入队（requeue=True）

        # 使用print确保日志能立即看到


        if parent_execution_id:
            for idx, script in enumerate(plan_scripts):

        # 在新线程中执行任务
        thread = threading.Thread(
            target=self._execute_task_thread,
            args=(task_data,),
            daemon=True,
            name=f"Task-{task_id}"
        )
        thread.start()

        return True  # 返回 True 表示任务已接收（ACK），不等待执行完成

    def _execute_task_thread(self, task_data: Dict[str, Any]):
        """
        在单独线程中执行任务

        Args:
            task_data: 任务数据
        """
        task_id = task_data.get("task_id", "")
        execution_id = task_data.get("execution_id")
        script_data = task_data.get("script_data", {})
        variables = task_data.get("variables", {})
        browser_type = task_data.get("browser_type", self.config.default_browser)

        # 【修复】任务已在 on_task_received 中加入 running_tasks
        # 这里只更新状态为 running，不再重复创建
        if task_id in self.running_tasks:
            self.running_tasks[task_id]["status"] = "running"
            self.running_tasks[task_id]["script_data"] = script_data
        else:
            # 异常情况：任务不在 running_tasks 中，可能是并发问题
            logger.warning(f"任务 {task_id} 不在 running_tasks 中，添加它")
            self.running_tasks[task_id] = {
                "execution_id": execution_id,
                "script_name": script_data.get("name", "未命名脚本"),
                "status": "running",
                "script_data": script_data
            }

        # 如果是计划执行，保存计划信息（用于GUI显示）
        parent_execution_id = script_data.get("parent_execution_id")
        plan_scripts = script_data.get("plan_scripts", [])

        if parent_execution_id and plan_scripts:
            if parent_execution_id not in self.plan_executions:
                plan_name = script_data.get("plan_name", "未知计划")
                execution_mode = script_data.get("execution_mode", "parallel")

                self.plan_executions[parent_execution_id] = {
                    "plan_name": plan_name,
                    "execution_mode": execution_mode,
                    "scripts": []
                }
                # 初始化所有脚本状态
                for idx, script in enumerate(plan_scripts):
                    self.plan_executions[parent_execution_id]["scripts"].append({
                        "id": script.get("id"),
                        "name": script.get("name"),
                        "status": "waiting",
                        "index": idx
                    })
            else:

            # 更新当前脚本状态为 running
            script_index = script_data.get("script_index", -1)
            if 0 <= script_index < len(self.plan_executions[parent_execution_id]["scripts"]):
                old_status = self.plan_executions[parent_execution_id]["scripts"][script_index]["status"]
                self.plan_executions[parent_execution_id]["scripts"][script_index]["status"] = "running"
                script_name = self.plan_executions[parent_execution_id]['scripts'][script_index]['name']
        else:

        # 初始化结果变量
        result = None

        # 每个线程创建自己的 executor 实例（避免并发冲突）
        executor = None

        try:
            # 检查任务是否已被取消
            if task_id in self.cancelled_tasks:
                raise Exception("任务已被取消")

            # 启动浏览器
            logger.info(f"任务 {task_id}: 正在启动 {browser_type} 浏览器...")
            executor = ScriptExecutor()
            if not executor.start(browser_type):
                raise Exception("浏览器启动失败")

            logger.info(f"任务 {task_id}: 浏览器启动成功")

            # 执行脚本
            result = self._execute_script(task_id, script_data, variables, executor)

            # 构建日志数据
            logs = []
            for step_result in result.get("steps", []):
                log_entry = {
                    "step": step_result.get("step_index", 0) + 1,
                    "level": "INFO" if step_result.get("success") else "ERROR",
                    "message": step_result.get("message", ""),
                    "timestamp": time.strftime("%H:%M:%S")
                }
                logs.append(log_entry)

            # 上报结果到平台
            self._send_task_result(task_id, {
                "status": "completed" if result["success"] else "failed",
                "message": result["message"],
                "steps": result.get("steps", []),
                "duration": result.get("duration", 0),
                "logs": logs
            })

            if result["success"]:
                logger.info(f"任务 {task_id} 执行成功")
            else:
                logger.error(f"任务 {task_id} 执行失败: {result['message']}")

        except Exception as e:
            logger.exception(f"任务 {task_id} 执行异常")
            error_msg = f"执行异常: {str(e)}"

            # 上报失败结果
            self._send_task_result(task_id, {
                "status": "failed",
                "message": error_msg,
                "error": traceback.format_exc()
            })

        finally:
            # 关闭浏览器（使用局部 executor 变量）
            if executor:
                try:
                    executor.stop()
                except:
                    pass

            # 获取任务信息，用于检查是否有等待的任务
            task_info = self.running_tasks.get(task_id, {})
            script_data = task_info.get("script_data", {})
            parent_execution_id = script_data.get("parent_execution_id")
            script_index = script_data.get("script_index", -1)

            # 清理任务
            self.running_tasks.pop(task_id, None)
            self.cancelled_tasks.discard(task_id)

            # 确定最终状态
            if result is not None:
                final_status = "completed" if result.get("success", False) else "failed"
                final_message = result.get("message", "")
            else:
                final_status = "failed"
                final_message = "执行失败"

            # 【关键修复】更新 plan_executions 中的脚本状态
            if parent_execution_id and parent_execution_id in self.plan_executions:
                if 0 <= script_index < len(self.plan_executions[parent_execution_id]["scripts"]):
                    old_status = self.plan_executions[parent_execution_id]["scripts"][script_index]["status"]
                    self.plan_executions[parent_execution_id]["scripts"][script_index]["status"] = final_status
                    logger.info(f"任务完成后更新脚本状态: index={script_index}, {old_status} -> {final_status}")

            # 【关键修复】检查并触发等待队列中的下一个任务
            if parent_execution_id:
                logger.info(f"任务 {task_id} 完成，parent_id={parent_execution_id}，检查等待队列")
                self._process_sequential_queue(parent_execution_id)

            # 调用任务完成回调
            if self.on_task_complete:
                try:
                    self.on_task_complete(task_id, final_status, final_message)
                except Exception as e:
                    logger.error(f"任务完成回调失败: {e}")

            logger.info(f"任务结束: {task_id}")

    def _execute_script(
        self,
        task_id: str,
        script_data: Dict[str, Any],
        variables: Dict[str, Any],
        executor: ScriptExecutor
    ) -> Dict[str, Any]:
        """
        执行脚本

        Args:
            task_id: 任务ID
            script_data: 脚本数据
            variables: 变量字典
            executor: ScriptExecutor 实例（每个线程独立）

        Returns:
            执行结果
        """
        steps = script_data.get("steps", [])
        script_name = script_data.get("name", "未命名脚本")

        logger.info(f"任务 {task_id}: 脚本 '{script_name}' 共有 {len(steps)} 个步骤")

        results = []
        all_success = True
        import time
        start_time = time.time()

        for index, step in enumerate(steps):
            # 检查任务是否被取消
            if task_id in self.cancelled_tasks:
                return {
                    "success": False,
                    "message": "任务已被取消",
                    "steps": results,
                    "cancelled": True
                }

            step_name = step.get("name", f"步骤{index + 1}")
            step_type = step.get("type", "")
            step_start_time = time.time()

            logger.info(f"任务 {task_id}: 执行步骤 {index + 1}/{len(steps)}: {step_name} ({step_type})")

            # 执行步骤
            step_result = executor.step_executor.execute(step, variables)

            # 计算步骤耗时（毫秒）
            step_duration = round((time.time() - step_start_time) * 1000, 2)

            # 添加步骤详细信息
            step_result["name"] = step_name
            step_result["type"] = step_type
            step_result["duration"] = step_duration
            step_result["step_index"] = index

            results.append(step_result)

            # 发送步骤日志
            if step_result["success"]:
                logger.info(f"任务 {task_id}: 步骤成功: {step_name} (耗时: {step_duration}ms)")
            else:
                logger.error(f"任务 {task_id}: 步骤失败: {step_name} - {step_result.get('message', 'Unknown error')}")

                # 失败立即上传截图
                if "screenshot" in step_result and step_result["screenshot"]:
                    self._send_screenshot(task_id, step_result["screenshot"], is_failure=True)

                all_success = False
                break

        end_time = time.time()
        duration = end_time - start_time

        if all_success:
            return {
                "success": True,
                "message": "脚本执行成功",
                "steps": results,
                "duration": round(duration, 2)
            }
        else:
            return {
                "success": False,
                "message": "脚本执行失败",
                "steps": results,
                "duration": round(duration, 2)
            }

    def _send_task_result(self, task_id: str, result: Dict[str, Any]):
        """发送任务执行结果到平台"""
        try:
            import json
            api_base = self.config.server_url.rstrip('/')
            result_url = f"{api_base}/api/tasks/{task_id}/result/"

            # 【关键修复】后端期望的是 status 字段 ('completed'/'failed')，不是 success 字段
            # 将 success: True/False 转换为 status: 'completed'/'failed'
            if "success" in result:
                is_success = result.pop("success")
                result["status"] = "completed" if is_success else "failed"

            # 清理数据：从步骤中移除截图数据（截图已单独发送）
            # 截图数据会导致 JSON 解析错误或数据过大
            if "steps" in result:
                # 创建新的 steps 列表，避免修改原始数据
                cleaned_steps = []
                for step in result["steps"]:
                    cleaned_step = {}
                    for key, value in step.items():
                        # 只保留需要的字段，确保值是 JSON 可序列化的
                        if key in ["name", "type", "success", "message", "duration", "step_index"]:
                            # 确保字符串值中的特殊字符被正确处理
                            if isinstance(value, str):
                                # 移除可能导致 JSON 解析错误的控制字符
                                cleaned_step[key] = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
                            else:
                                cleaned_step[key] = value
                    cleaned_steps.append(cleaned_step)
                result["steps"] = cleaned_steps

            # 移除其他可能有问题的字段
            result.pop("error", None)
            result.pop("logs", None)  # logs 可能包含特殊字符

            # 使用 default=str 处理非序列化对象，让 json.dumps 自动处理转义
            try:
                json_data = json.dumps(result, ensure_ascii=False, default=str)
            except Exception as e:
                logger.error(f"JSON 序列化失败: {e}")
                # 降级：只发送基本信息
                simple_result = {
                    "status": result.get("status", "failed"),
                    "message": "JSON序列化失败",
                    "duration": result.get("duration", 0)
                }
                json_data = json.dumps(simple_result, ensure_ascii=False)

            # 调试：打印完整 JSON 数据
            # 【关键修复】使用 json 参数而不是 data 参数
            # requests 库会自动设置正确的 Content-Length 和 Content-Type 头
            # 避免 JSON 数据在传输过程中被截断
            response = requests.post(
                result_url,
                json=result,  # 直接传入字典，让 requests 自动序列化
                timeout=10
            )

            # 检查响应状态码
            if response.status_code == 200:
                logger.info(f"任务结果已上报: {task_id}")

                # 主动请求后端分发新任务（确保并发任务能立即开始）
                try:
                    distribute_url = f"{api_base}/api/tasks/distribute/"
                    dist_response = requests.post(
                        distribute_url,
                        json={},
                        headers={'Content-Type': 'application/json; charset=utf-8'},
                        timeout=5
                    )
                    if dist_response.status_code == 200:
                        logger.info(f"已请求后端分发新任务")
                    else:
                        logger.warning(f"请求分发失败: HTTP {dist_response.status_code}")
                except Exception as dist_e:
                    logger.warning(f"请求分发异常: {dist_e}")
            else:
                logger.error(f"上报任务结果失败: {task_id}, HTTP {response.status_code}")
                logger.error(f"响应内容: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"上报任务结果网络失败: {task_id}, {e}")
        except Exception as e:
            logger.error(f"上报任务结果失败: {task_id}, {e}")

    def _process_sequential_queue(self, parent_execution_id: str):
        """
        处理顺序执行队列，触发下一个任务

        Args:
            parent_execution_id: 父执行ID
        """

        with self._wait_lock:
            if parent_execution_id in self._sequential_wait_queue:
                wait_queue = self._sequential_wait_queue[parent_execution_id]
                if wait_queue:
                    # 获取下一个等待的任务
                    next_task_data = wait_queue.pop(0)
                    next_task_id = next_task_data.get("task_id", "")

                    # 如果队列为空，删除队列
                    if not wait_queue:
                        del self._sequential_wait_queue[parent_execution_id]

                    logger.info(f"从等待队列中取下一个任务: {next_task_id}")

                    # 在新线程中执行下一个任务
                    thread = threading.Thread(
                        target=self._execute_task_thread,
                        args=(next_task_data,),
                        daemon=True,
                        name=f"Task-{next_task_id}"
                    )
                    thread.start()
                else:
            else:

    def _send_screenshot(self, task_id: str, image_data: str, is_failure: bool = True):
        """发送截图到平台"""
        try:
            api_base = self.config.server_url.rstrip('/')
            screenshot_url = f"{api_base}/api/tasks/{task_id}/screenshot/"

            # 【关键修复】使用 json 参数，requests 会自动处理序列化和 Content-Length
            requests.post(
                screenshot_url,
                json={
                    "image_data": image_data,
                    "is_failure": is_failure
                },
                timeout=10
            )
            logger.info(f"截图已上报: {task_id}")

        except Exception as e:
            logger.error(f"上报截图失败: {e}")

    def on_mq_connected(self):
        """消息队列连接成功回调"""
        logger.info("消息队列已连接")

    def on_mq_disconnected(self):
        """消息队列断开连接回调"""
        logger.warning("消息队列已断开")

    def on_mq_error(self, error):
        """消息队列错误回调"""
        logger.error(f"消息队列错误: {error}")

    def disconnect(self):
        """断开连接"""
        logger.info("正在断开连接...")

        # 停止心跳
        self._is_heartbeat_running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)

        # 停止消息队列消费者
        self.mq_consumer.stop()

        # 取消所有正在执行的任务
        for task_id in list(self.running_tasks.keys()):
            self.cancelled_tasks.add(task_id)

        logger.info("任务管理器已断开连接")


# 单例
_task_manager_v2: Optional[TaskManagerV2] = None


def get_task_manager_v2() -> TaskManagerV2:
    """获取任务管理器 V2 单例"""
    global _task_manager_v2
    if _task_manager_v2 is None:
        _task_manager_v2 = TaskManagerV2()
    return _task_manager_v2
