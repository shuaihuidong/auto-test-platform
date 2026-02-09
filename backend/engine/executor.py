"""
测试执行器
负责协调整个测试执行流程
"""
import time
from datetime import datetime
from django.utils import timezone
from typing import Dict, Any
import logging

from .base import TestEngine
from .selenium_engine import SeleniumEngine
from .playwright_engine import PlaywrightEngine
from .appium_engine import AppiumEngine
from .api_engine import ApiEngine
from apps.executions.models import Execution
from apps.scripts.models import Script, DataSource
from apps.reports.generators import ReportGenerator

logger = logging.getLogger(__name__)


class TestExecutor:
    """
    测试执行器
    负责执行测试脚本/计划并生成报告
    """

    def __init__(self, execution: Execution):
        self.execution = execution
        self.script = execution.script
        self.engine = None
        self.debug_mode = execution.debug_mode
        self.breakpoints = set(execution.breakpoints or [])
        self.paused = False
        self.stopped = False
        self.step_by_step = False
        self.current_step_index = 0

    def run(self):
        """执行测试"""
        try:
            # 更新状态为运行中
            self.execution.status = 'running'
            self.execution.started_at = timezone.now()
            self.execution.save()

            # 初始化测试引擎
            if not self._setup_engine():
                self._mark_failed('引擎初始化失败')
                return

            # 获取测试步骤
            steps = self._get_steps()
            if not steps:
                self._mark_failed('没有可执行的步骤')
                return

            # 执行测试
            if self.debug_mode:
                result = self._run_debug_mode(steps)
            else:
                result = self.engine.execute_steps(steps)

            # 更新执行结果
            if not self.stopped:
                self.execution.result = result
                self.execution.status = 'completed' if result['failed'] == 0 else 'failed'
                self.execution.completed_at = timezone.now()

                # 保存变量快照
                if hasattr(self.engine, 'variables'):
                    self.execution.variables_snapshot = self.engine.variables.copy()

                self.execution.save()

            # 生成报告
            if not self.debug_mode:
                try:
                    report_generator = ReportGenerator(self.execution)
                    report_generator.generate()
                except Exception as e:
                    logger.error(f"生成报告失败: {str(e)}")

        except Exception as e:
            logger.error(f"执行测试异常: {str(e)}")
            self._mark_failed(str(e))

        finally:
            # 清理引擎资源
            if self.engine:
                try:
                    self.engine.teardown()
                except Exception as e:
                    logger.error(f"清理引擎资源失败: {str(e)}")

    def _run_debug_mode(self, steps: list) -> dict:
        """调试模式执行"""
        result = {'total': len(steps), 'passed': 0, 'failed': 0, 'steps': [], 'logs': []}

        for index, step in enumerate(steps):
            # 检查是否停止
            if self.stopped:
                self.execution.status = 'stopped'
                self.execution.save()
                break

            self.current_step_index = index
            self.execution.current_step_index = index
            self.execution.save()

            # 检查断点
            if index in self.breakpoints:
                self.paused = True
                self.execution.status = 'paused'
                self.execution.save()

                # 等待恢复
                while self.paused and not self.stopped:
                    import time
                    time.sleep(0.5)

                if self.stopped:
                    break

            # 检查单步执行
            if self.step_by_step and index > 0:
                self.paused = True
                self.execution.status = 'paused'
                self.execution.save()

                while self.paused and not self.stopped:
                    import time
                    time.sleep(0.5)

                if self.stopped:
                    break

            # 执行步骤
            try:
                step_result = self.engine.execute_step(step)
                result['steps'].append(step_result)

                if step_result.get('success'):
                    result['passed'] += 1
                else:
                    result['failed'] += 1

            except Exception as e:
                result['failed'] += 1
                result['steps'].append({
                    'success': False,
                    'error': str(e)
                })

        return result

    def pause(self):
        """暂停执行"""
        self.paused = True
        self.execution.status = 'paused'
        self.execution.save()

    def resume(self):
        """恢复执行"""
        self.paused = False
        self.step_by_step = False
        if self.execution.status == 'paused':
            self.execution.status = 'running'
            self.execution.save()

    def stop(self):
        """停止执行"""
        self.stopped = True
        self.paused = False
        self.execution.status = 'stopped'
        self.execution.completed_at = timezone.now()
        self.execution.save()

    def step(self):
        """单步执行"""
        self.step_by_step = True
        self.paused = False
        if self.execution.status == 'paused':
            self.execution.status = 'running'
            self.execution.save()

    def get_variables(self) -> dict:
        """获取当前变量"""
        if hasattr(self.engine, 'variables'):
            return self.engine.variables.copy()
        return {}

    def set_breakpoint(self, step_index: int):
        """设置断点"""
        self.breakpoints.add(step_index)
        self.execution.breakpoints = list(self.breakpoints)
        self.execution.save()

    def remove_breakpoint(self, step_index: int):
        """移除断点"""
        self.breakpoints.discard(step_index)
        self.execution.breakpoints = list(self.breakpoints)
        self.execution.save()

    def _setup_engine(self) -> bool:
        """初始化测试引擎"""
        framework = self.script.framework

        # 获取配置
        config = self._get_engine_config()

        # 根据框架创建引擎
        if framework == 'selenium':
            self.engine = SeleniumEngine(config)
        elif framework == 'playwright':
            self.engine = PlaywrightEngine(config)
        elif framework == 'appium':
            self.engine = AppiumEngine(config)
        elif framework == 'httprunner':
            self.engine = ApiEngine(config)
        else:
            self.execution.result = {'error': f'不支持的框架: {framework}'}
            return False

        # 初始化引擎
        return self.engine.setup()

    def _get_engine_config(self) -> Dict[str, Any]:
        """获取引擎配置"""
        config = {}

        # 从脚本获取全局变量
        config['variables'] = getattr(self.script, 'variables', {}) or {}

        if self.script.framework == 'selenium':
            config['browser'] = 'chrome'  # 可从配置中读取
            config['headless'] = False
            config['timeout'] = getattr(self.script, 'timeout', 30000) / 1000  # 转换为秒
            config['screenshot_on_failure'] = True
            config['continue_on_failure'] = True
            config['retry_count'] = getattr(self.script, 'retry_count', 0)

        elif self.script.framework == 'playwright':
            config['browser'] = 'chromium'
            config['headless'] = False
            config['timeout'] = getattr(self.script, 'timeout', 30000)  # Playwright使用毫秒
            config['retry_count'] = getattr(self.script, 'retry_count', 0)

        elif self.script.framework == 'appium':
            config['platform'] = 'android'
            config['appium_server'] = 'http://localhost:4723'

        elif self.script.framework == 'httprunner':
            config['base_url'] = ''  # 可从脚本步骤中获取
            config['timeout'] = getattr(self.script, 'timeout', 30000) / 1000

        return config

    def _get_steps(self) -> list:
        """获取测试步骤（处理模块和数据驱动）"""
        steps = self.script.steps.copy()

        # 如果是参数化测试，处理数据源
        if self.script.data_driven and self.script.data_source:
            return self._process_data_driven_steps(steps)

        # 展开模块步骤
        return self._expand_modules(steps)

    def _expand_modules(self, steps: list) -> list:
        """展开模块步骤"""
        expanded_steps = []

        for step in steps:
            if step.get('type') == 'module':
                # 获取模块脚本
                module_script_id = step.get('module_id')
                if module_script_id:
                    try:
                        module_script = Script.objects.get(id=module_script_id, is_module=True)
                        # 递归展开模块
                        module_steps = self._expand_modules(module_script.steps)
                        expanded_steps.extend(module_steps)
                    except Script.DoesNotExist:
                        logger.warning(f"模块脚本 {module_script_id} 不存在")
            else:
                expanded_steps.append(step)

        return expanded_steps

    def _process_data_driven_steps(self, steps: list) -> list:
        """处理数据驱动测试"""
        data_source = self.script.data_source
        if not data_source:
            return steps

        data = data_source.data
        if not isinstance(data, dict) or 'rows' not in data:
            return steps

        # 为每一行数据创建一组步骤
        all_steps = []
        for row_index, row_data in enumerate(data['rows']):
            # 替换步骤中的变量
            row_steps = self._replace_variables(steps, row_data, row_index)
            all_steps.extend(row_steps)

        return all_steps

    def _replace_variables(self, steps: list, variables: dict, row_index: int) -> list:
        """替换步骤中的变量"""
        import json
        import re

        steps_json = json.dumps(steps)

        # 替换 ${variable} 格式的变量
        for key, value in variables.items():
            placeholder = f'${{{key}}}'
            steps_json = steps_json.replace(placeholder, str(value))

        # 解析回步骤列表
        new_steps = json.loads(steps_json)

        # 为每个步骤添加数据行标识
        for step in new_steps:
            step['_data_row'] = row_index

        return new_steps

    def _mark_failed(self, error_msg: str):
        """标记执行失败"""
        self.execution.status = 'failed'
        self.execution.completed_at = timezone.now()
        self.execution.result = {
            'total': 0,
            'passed': 0,
            'failed': 1,
            'steps': [],
            'error': error_msg
        }
        self.execution.save()


class PlanExecutor:
    """
    计划执行器
    负责执行测试计划（包含多个脚本）
    """

    def __init__(self, plan):
        self.plan = plan

    def run(self):
        """执行计划中的所有脚本"""
        from apps.executions.models import Execution
        from apps.scripts.models import Script

        results = {
            'total_scripts': 0,
            'completed_scripts': 0,
            'failed_scripts': 0,
            'executions': []
        }

        # 获取计划中的所有脚本
        script_ids = self.plan.script_ids or []
        scripts = Script.objects.filter(id__in=script_ids)

        results['total_scripts'] = scripts.count()

        # 执行每个脚本
        for script in scripts:
            # 创建执行记录
            execution = Execution.objects.create(
                plan=self.plan,
                script=script,
                status='pending',
                created_by=self.plan.created_by
            )

            # 执行脚本
            executor = TestExecutor(execution)
            executor.run()

            # 统计结果
            execution.refresh_from_db()
            results['executions'].append(execution.id)

            if execution.status == 'completed':
                results['completed_scripts'] += 1
            else:
                results['failed_scripts'] += 1

        return results
