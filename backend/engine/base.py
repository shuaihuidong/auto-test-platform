"""
测试引擎基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import re


class TestEngine(ABC):
    """
    测试引擎抽象基类
    所有测试引擎必须实现此接口
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.driver = None
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'steps': [],
            'logs': [],
            'screenshots': []
        }
        self.current_step_index = 0
        self.variables = config.get('variables', {}) if config else {}

    @abstractmethod
    def setup(self) -> bool:
        """
        初始化测试环境
        返回: bool - 是否初始化成功
        """
        pass

    @abstractmethod
    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个测试步骤

        参数:
            step: 步骤数据，包含:
                - type: 步骤类型
                - params: 步骤参数
                - name: 步骤名称

        返回:
            Dict: 执行结果，包含:
                - success: bool - 是否成功
                - message: str - 结果消息
                - error: str - 错误信息(如果失败)
                - screenshot: str - 截图路径(如果有)
        """
        pass

    @abstractmethod
    def teardown(self) -> None:
        """
        清理测试环境
        """
        pass

    @abstractmethod
    def get_result(self) -> Dict[str, Any]:
        """
        获取测试结果

        返回:
            Dict: 测试结果汇总
        """
        pass

    def add_log(self, message: str, level: str = 'info'):
        """添加日志"""
        self.results['logs'].append({
            'step': self.current_step_index,
            'message': message,
            'level': level,
            'timestamp': self._get_timestamp()
        })

    def add_screenshot(self, path: str):
        """添加截图"""
        self.results['screenshots'].append({
            'step': self.current_step_index,
            'path': path
        })

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _find_element(self, locator: Dict[str, str]):
        """
        查找元素（子类可实现自己的定位逻辑）

        参数:
            locator: 定位器，包含:
                - type: 定位类型 (xpath, id, name, class, css)
                - value: 定位值
        """
        raise NotImplementedError("子类必须实现_find_element方法")

    def set_variable(self, name: str, value: Any) -> None:
        """
        设置变量

        参数:
            name: 变量名
            value: 变量值
        """
        self.variables[name] = value
        self.add_log(f"设置变量: {name} = {value}")

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        获取变量

        参数:
            name: 变量名
            default: 默认值

        返回:
            变量值，如果不存在则返回默认值
        """
        return self.variables.get(name, default)

    def resolve_variables(self, value: Any) -> Any:
        """
        解析变量替换，支持 ${变量名} 格式

        参数:
            value: 需要解析的值（可以是字符串、字典、列表等）

        返回:
            解析后的值
        """
        if isinstance(value, str):
            # 使用正则表达式查找所有 ${变量名} 格式的变量
            pattern = r'\$\{([^}]+)\}'

            def replace_var(match):
                var_name = match.group(1)
                var_value = self.get_variable(var_name, '')
                return str(var_value) if var_value is not None else match.group(0)

            return re.sub(pattern, replace_var, value)
        elif isinstance(value, dict):
            return {k: self.resolve_variables(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.resolve_variables(item) for item in value]
        else:
            return value

    def extract_from_text(self, text: str, pattern: str, pattern_type: str = 'regex') -> Any:
        """
        从文本中提取数据

        参数:
            text: 源文本
            pattern: 提取模式（正则表达式、JSON路径等）
            pattern_type: 提取类型（regex, json_path, css_selector）

        返回:
            提取的结果
        """
        try:
            if pattern_type == 'regex':
                match = re.search(pattern, text)
                if match:
                    # 如果有捕获组，返回第一个捕获组，否则返回整个匹配
                    return match.group(1) if match.groups() else match.group(0)
                return None
            # 可以扩展其他提取类型
            else:
                return None
        except Exception as e:
            self.add_log(f"提取数据失败: {str(e)}", 'error')
            return None

    def evaluate_condition(self, condition: str) -> bool:
        """
        评估条件表达式

        支持:
        - 变量比较: ${var1} == ${var2}
        - 数值比较: ${count} > 5
        - 字符串比较: ${status} == 'success'
        - 布尔运算: ${flag} == true
        - 逻辑运算: and, or, not

        参数:
            condition: 条件表达式字符串

        返回:
            bool: 条件是否为真
        """
        try:
            # 解析变量
            resolved_condition = self.resolve_variables(condition)

            # 处理布尔值
            resolved_condition = resolved_condition.replace(' true', ' True').replace(' false', ' False')

            # 处理字符串引号
            resolved_condition = resolved_condition.replace("'true'", "True").replace("'false'", "False")

            # 安全评估（仅允许有限的操作）
            allowed_names = {"True": True, "False": False, "None": None}
            allowed_names.update(self.variables)

            # 使用eval进行评估，限制可用名称
            result = eval(resolved_condition, {"__builtins__": {}}, allowed_names)

            return bool(result)

        except Exception as e:
            self.add_log(f"条件评估失败: {str(e)}", 'error')
            return False

    def execute_control_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行流程控制步骤

        支持的步骤类型:
        - if: 条件判断
        - loop: 循环执行
        - retry: 失败重试
        - skip: 跳过步骤

        参数:
            step: 流程控制步骤

        返回:
            Dict: 执行结果
        """
        step_type = step.get('type')
        params = step.get('params', {})

        if step_type == 'if':
            return self._execute_if_step(step)
        elif step_type == 'loop':
            return self._execute_loop_step(step)
        elif step_type == 'retry':
            return self._execute_retry_step(step)
        elif step_type == 'skip':
            return {'success': True, 'message': '步骤已跳过', 'skipped': True}
        else:
            return {
                'success': False,
                'error': f'未知的流程控制类型: {step_type}'
            }

    def _execute_if_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行条件判断步骤

        示例:
        {
            "type": "if",
            "params": {
                "condition": "${status} == 'success'"
            },
            "children": [...]
        }
        """
        params = step.get('params', {})
        condition = params.get('condition')

        if not condition:
            return {'success': False, 'error': '缺少condition参数'}

        # 评估条件
        condition_met = self.evaluate_condition(condition)

        if condition_met:
            # 条件为真，执行子步骤
            children = step.get('children', [])
            if children:
                return self.execute_steps(children)
            return {'success': True, 'message': '条件为真，但无子步骤执行'}
        else:
            return {'success': True, 'message': '条件为假，跳过子步骤', 'skipped': True}

    def _execute_loop_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行循环步骤

        支持两种循环类型:
        1. count: 固定次数循环
        2. data: 遍历数据数组

        示例:
        {
            "type": "loop",
            "params": {
                "loop_type": "count",
                "count": 5
            },
            "children": [...]
        }

        或:
        {
            "type": "loop",
            "params": {
                "loop_type": "data",
                "data_variable": "items"
            },
            "children": [...]
        }
        """
        params = step.get('params', {})
        loop_type = params.get('loop_type', 'count')
        children = step.get('children', [])

        if not children:
            return {'success': False, 'error': '循环步骤缺少子步骤'}

        results = {
            'success': True,
            'total_iterations': 0,
            'passed_iterations': 0,
            'failed_iterations': 0,
            'message': ''
        }

        if loop_type == 'count':
            # 固定次数循环
            count = params.get('count', 1)
            for i in range(count):
                self.add_log(f"循环第 {i + 1}/{count} 次")
                self.set_variable('__loop_index__', i)
                self.set_variable('__loop_count__', count)

                iteration_result = self.execute_steps(children)
                results['total_iterations'] += 1

                if iteration_result.get('failed', 0) > 0:
                    results['failed_iterations'] += 1
                else:
                    results['passed_iterations'] += 1

            results['message'] = f'循环完成: 共 {count} 次，成功 {results["passed_iterations"]} 次，失败 {results["failed_iterations"]} 次'
            return results

        elif loop_type == 'data':
            # 遍历数据数组
            data_variable = params.get('data_variable')
            data = params.get('data')

            if data_variable:
                # 从变量中获取数据
                data = self.get_variable(data_variable, [])

            if not isinstance(data, list):
                return {'success': False, 'error': '数据必须是数组类型'}

            for i, item in enumerate(data):
                self.add_log(f"遍历数据第 {i + 1}/{len(data)} 项")
                self.set_variable('__loop_item__', item)
                self.set_variable('__loop_index__', i)

                iteration_result = self.execute_steps(children)
                results['total_iterations'] += 1

                if iteration_result.get('failed', 0) > 0:
                    results['failed_iterations'] += 1
                else:
                    results['passed_iterations'] += 1

            results['message'] = f'数据遍历完成: 共 {len(data)} 项，成功 {results["passed_iterations"]} 次，失败 {results["failed_iterations"]} 次'
            return results

        else:
            return {'success': False, 'error': f'未知的循环类型: {loop_type}'}

    def _execute_retry_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行重试步骤

        示例:
        {
            "type": "retry",
            "params": {
                "max_retries": 3,
                "retry_interval": 1000
            },
            "children": [...]
        }
        """
        params = step.get('params', {})
        max_retries = params.get('max_retries', 3)
        retry_interval = params.get('retry_interval', 1000)  # 毫秒
        children = step.get('children', [])

        if not children:
            return {'success': False, 'error': '重试步骤缺少子步骤'}

        for attempt in range(max_retries + 1):
            if attempt > 0:
                self.add_log(f"重试第 {attempt} 次")
                import time
                time.sleep(retry_interval / 1000)

            self.set_variable('__retry_count__', attempt)

            result = self.execute_steps(children)

            # 如果所有步骤都成功，返回成功
            if result.get('failed', 0) == 0:
                return {
                    'success': True,
                    'message': f'执行成功（尝试 {attempt + 1}/{max_retries + 1} 次）',
                    'attempts': attempt + 1
                }

        # 所有重试都失败
        return {
            'success': False,
            'error': f'执行失败，已重试 {max_retries} 次',
            'attempts': max_retries + 1
        }

    def execute_steps(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行多个步骤

        参数:
            steps: 步骤列表

        返回:
            Dict: 所有步骤的执行结果
        """
        self.results['total'] = len(steps)

        for index, step in enumerate(steps):
            self.current_step_index = index

            # 解析步骤中的变量
            resolved_step = self.resolve_variables(step)

            self.add_log(f"开始执行步骤 {index + 1}: {resolved_step.get('name', 'Unnamed')}")

            try:
                # 检查是否是流程控制步骤
                step_type = resolved_step.get('type')
                if step_type in ['if', 'loop', 'retry', 'skip']:
                    result = self.execute_control_step(resolved_step)
                else:
                    result = self.execute_step(resolved_step)

                step_result = {
                    'index': index,
                    'name': step.get('name', 'Unnamed'),
                    'type': step.get('type', 'unknown'),
                    'success': result.get('success', False),
                    'message': result.get('message', ''),
                    'duration': result.get('duration', 0)
                }

                # 处理流程控制步骤的特殊结果
                if step_type in ['if', 'loop', 'retry']:
                    # 流程控制步骤可能有嵌套的结果
                    if 'total_iterations' in result:
                        step_result['iterations'] = result['total_iterations']
                        step_result['passed_iterations'] = result.get('passed_iterations', 0)
                        step_result['failed_iterations'] = result.get('failed_iterations', 0)
                    if 'attempts' in result:
                        step_result['attempts'] = result['attempts']
                    if result.get('skipped'):
                        step_result['skipped'] = True

                if result.get('error'):
                    step_result['error'] = result['error']
                    self.results['failed'] += 1
                    self.add_log(f"步骤失败: {result['error']}", 'error')
                else:
                    self.results['passed'] += 1
                    self.add_log(f"步骤成功: {result.get('message', '')}")

                if result.get('screenshot'):
                    self.add_screenshot(result['screenshot'])

                self.results['steps'].append(step_result)

                # 如果步骤失败且不继续执行，则中断
                if not result.get('success') and not self.config.get('continue_on_failure', True):
                    self.add_log("步骤失败，停止执行", 'error')
                    break

            except Exception as e:
                self.results['failed'] += 1
                error_msg = f"步骤执行异常: {str(e)}"
                self.add_log(error_msg, 'error')
                self.results['steps'].append({
                    'index': index,
                    'name': step.get('name', 'Unnamed'),
                    'type': step.get('type', 'unknown'),
                    'success': False,
                    'error': error_msg
                })
                if not self.config.get('continue_on_failure', True):
                    break

        return self.results

    def _execute_upload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文件上传步骤

        参数:
            params: 包含:
                - locator: 文件输入元素定位器
                - file_path: 要上传的文件路径

        返回:
            执行结果
        """
        raise NotImplementedError("子类必须实现_execute_upload方法")

    def _execute_download(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文件下载步骤

        参数:
            params: 包含:
                - url: 下载链接URL
                - save_path: 保存路径（可选）

        返回:
            执行结果
        """
        raise NotImplementedError("子类必须实现_execute_download方法")
