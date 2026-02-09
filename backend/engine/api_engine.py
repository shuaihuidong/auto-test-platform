"""
API测试引擎实现
"""
import time
import json
from typing import Dict, Any, List
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

from .base import TestEngine


class ApiEngine(TestEngine):
    """
    API测试引擎
    支持RESTful API测试
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.timeout = self.config.get('timeout', 30)
        self.base_url = self.config.get('base_url', '')
        self.headers = self.config.get('headers', {})
        self.auth = self.config.get('auth', {})
        self.session = requests.Session()
        self.cookies = {}

    def setup(self) -> bool:
        """初始化API测试环境"""
        try:
            # 设置默认headers
            if 'Content-Type' not in self.headers:
                self.headers['Content-Type'] = 'application/json'

            # 设置认证
            if self.auth.get('type') == 'basic':
                self.session.auth = HTTPBasicAuth(
                    self.auth.get('username'),
                    self.auth.get('password')
                )
            elif self.auth.get('type') == 'bearer':
                token = self.auth.get('token')
                if token:
                    self.headers['Authorization'] = f'Bearer {token}'

            self.session.headers.update(self.headers)

            self.add_log("API测试环境初始化成功")
            return True

        except Exception as e:
            self.add_log(f"API环境初始化失败: {str(e)}", 'error')
            return False

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """执行API测试步骤"""
        start_time = time.time()
        step_type = step.get('type')
        params = step.get('params', {})

        try:
            if step_type == 'request':
                result = self._request(params)
            elif step_type == 'assert':
                result = self._assert(params)
            elif step_type == 'extract':
                result = self._extract(params)
            elif step_type == 'wait':
                result = self._wait(params)
            elif step_type == 'set_variable':
                result = self._set_variable(params)
            else:
                result = {
                    'success': False,
                    'error': f'未知的步骤类型: {step_type}'
                }

            result['duration'] = round((time.time() - start_time) * 1000, 2)
            return result

        except Exception as e:
            return {
                'success': False,
                'error': f'步骤执行异常: {str(e)}',
                'duration': round((time.time() - start_time) * 1000, 2)
            }

    def teardown(self) -> None:
        """清理资源"""
        try:
            self.session.close()
            self.add_log("Session已关闭")
        except Exception as e:
            self.add_log(f"关闭session时出错: {str(e)}", 'error')

    def get_result(self) -> Dict[str, Any]:
        """获取测试结果"""
        return self.results

    def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送HTTP请求"""
        method = params.get('method', 'GET').upper()
        url = self._resolve_url(params.get('url', ''))
        headers = params.get('headers', {})
        body = params.get('body', {})
        params_dict = params.get('params', {})
        timeout = params.get('timeout', self.timeout)
        allow_redirects = params.get('allow_redirects', True)

        # 执行前置脚本
        pre_script = params.get('pre_request_script')
        if pre_script:
            script_result = self._execute_script(pre_script, {'params': params})
            if not script_result.get('success'):
                return script_result

        # 应用签名/加密
        if params.get('sign_enabled'):
            signing_result = self._apply_signing(params)
            if not signing_result.get('success'):
                return signing_result
            # 更新headers和body
            if signing_result.get('headers'):
                headers.update(signing_result['headers'])
            if signing_result.get('body'):
                body = signing_result['body']

        # 合并headers
        request_headers = self.headers.copy()
        request_headers.update(headers)

        # 准备请求
        request_params = {
            'headers': request_headers,
            'timeout': timeout,
            'allow_redirects': allow_redirects
        }

        if params_dict:
            request_params['params'] = self._resolve_variables(params_dict)

        # 处理body
        if body and method in ['POST', 'PUT', 'PATCH']:
            content_type = request_headers.get('Content-Type', 'application/json')
            if 'application/json' in content_type:
                request_params['json'] = self._resolve_variables(body)
            elif 'application/x-www-form-urlencoded' in content_type:
                request_params['data'] = self._resolve_variables(body)
            else:
                request_params['data'] = body

        # 发送请求
        response = self.session.request(method, url, **request_params)

        # 保存响应供后续使用
        self.last_response = response

        # 构建结果
        result = {
            'success': response.status_code < 400,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds() * 1000,
            'response_headers': dict(response.headers),
            'request': {
                'method': method,
                'url': url,
                'headers': request_headers
            }
        }

        # 尝试解析响应体
        try:
            response_body = response.json()
            result['response_body'] = response_body
        except:
            result['response_body'] = response.text

        # 判断请求是否成功（基于状态码）
        expected_status = params.get('expected_status', 200)
        if isinstance(expected_status, list):
            result['success'] = response.status_code in expected_status
        else:
            result['success'] = response.status_code == expected_status

        result['message'] = f'{method} {url} - {response.status_code}'

        # 执行后置脚本
        post_script = params.get('post_request_script')
        if post_script:
            post_result = self._execute_script(post_script, {
                'response': result,
                'response_obj': response
            })
            if not post_result.get('success'):
                return post_result

        return result

    def _assert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """断言响应"""
        assert_type = params.get('assert_type', 'status_code')
        expected = params.get('expected')

        if not hasattr(self, 'last_response'):
            return {'success': False, 'error': '没有可用的响应'}

        response = self.last_response

        try:
            if assert_type == 'status_code':
                actual = response.status_code
                if isinstance(expected, list):
                    success = actual in expected
                else:
                    success = actual == expected
                return {
                    'success': success,
                    'message': f'状态码断言: 期望={expected}, 实际={actual}',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'header':
                header_name = params.get('header_name')
                actual = response.headers.get(header_name)
                success = str(actual) == str(expected) if expected else actual is not None
                return {
                    'success': success,
                    'message': f'响应头断言 [{header_name}]: 期望="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'body':
                json_path = params.get('json_path')
                try:
                    response_body = response.json()
                    actual = self._get_json_value(response_body, json_path)
                    success = str(actual) == str(expected)
                    return {
                        'success': success,
                        'message': f'响应体断言 [{json_path}]: 期望="{expected}", 实际="{actual}"',
                        'expected': expected,
                        'actual': actual
                    }
                except:
                    return {'success': False, 'error': '无法解析JSON响应'}

            elif assert_type == 'body_contains':
                substring = params.get('substring', expected)
                response_text = response.text
                success = substring in response_text
                return {
                    'success': success,
                    'message': f'响应体包含断言: 查找="{substring}", 结果={success}',
                    'substring': substring
                }

            elif assert_type == 'not_contains':
                substring = params.get('substring', expected)
                response_text = response.text
                success = substring not in response_text
                return {
                    'success': success,
                    'message': f'响应体不包含断言: 查找不包含="{substring}", 结果={success}',
                    'substring': substring
                }

            elif assert_type == 'regex':
                pattern = params.get('pattern', expected)
                import re
                try:
                    compiled_pattern = re.compile(pattern)
                    success = compiled_pattern.search(response.text) is not None
                    return {
                        'success': success,
                        'message': f'正则匹配断言: pattern="{pattern}", 结果={success}',
                        'expected': pattern
                    }
                except re.error as e:
                    return {'success': False, 'error': f'正则表达式错误: {str(e)}'}

            elif assert_type == 'numeric_compare':
                json_path = params.get('json_path')
                operator = params.get('operator', '==')
                try:
                    response_body = response.json()
                    actual = self._get_json_value(response_body, json_path)

                    actual_num = float(str(actual).strip())
                    expected_num = float(str(expected).strip())

                    if operator == '==':
                        success = actual_num == expected_num
                    elif operator == '!=':
                        success = actual_num != expected_num
                    elif operator == '>':
                        success = actual_num > expected_num
                    elif operator == '>=':
                        success = actual_num >= expected_num
                    elif operator == '<':
                        success = actual_num < expected_num
                    elif operator == '<=':
                        success = actual_num <= expected_num
                    else:
                        return {'success': False, 'error': f'未知的比较运算符: {operator}'}

                    return {
                        'success': success,
                        'message': f'数值比较断言 [{json_path}]: 期望 {operator} {expected_num}, 实际={actual_num}',
                        'expected': expected_num,
                        'actual': actual_num
                    }
                except (ValueError, TypeError):
                    return {'success': False, 'error': '无法转换为数值进行比较'}

            elif assert_type == 'schema':
                # JSON Schema验证（需要jsonschema库）
                schema = params.get('schema')
                try:
                    import jsonschema
                    response_body = response.json()
                    jsonschema.validate(instance=response_body, schema=schema)
                    return {'success': True, 'message': 'JSON Schema验证通过'}
                except ImportError:
                    return {'success': False, 'error': '需要安装jsonschema库'}
                except Exception as e:
                    return {'success': False, 'error': f'Schema验证失败: {str(e)}'}

            elif assert_type == 'response_time':
                max_time = params.get('max_time', 1000)
                actual_time = response.elapsed.total_seconds() * 1000
                success = actual_time <= max_time
                return {
                    'success': success,
                    'message': f'响应时间断言: 最大={max_time}ms, 实际={actual_time:.2f}ms',
                    'expected': max_time,
                    'actual': actual_time
                }

            else:
                return {'success': False, 'error': f'未知的断言类型: {assert_type}'}

        except Exception as e:
            return {'success': False, 'error': f'断言失败: {str(e)}'}

    def _extract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """从响应中提取变量"""
        if not hasattr(self, 'last_response'):
            return {'success': False, 'error': '没有可用的响应'}

        variable_name = params.get('variable_name')
        extract_type = params.get('extract_type', 'json_path')
        value = None

        try:
            if extract_type == 'json_path':
                json_path = params.get('json_path')
                response_body = self.last_response.json()
                value = self._get_json_value(response_body, json_path)

            elif extract_type == 'header':
                header_name = params.get('header_name')
                value = self.last_response.headers.get(header_name)

            elif extract_type == 'regex':
                pattern = params.get('pattern')
                import re
                match = re.search(pattern, self.last_response.text)
                if match:
                    value = match.group(1) if match.lastindex else match.group(0)

            elif extract_type == 'cookie':
                cookie_name = params.get('cookie_name')
                value = self.last_response.cookies.get(cookie_name)

            # 保存到变量
            if variable_name:
                self.set_variable(variable_name, value)

            return {
                'success': True,
                'message': f'已提取变量 {variable_name} = {value}',
                'variable_name': variable_name,
                'value': value
            }

        except Exception as e:
            return {'success': False, 'error': f'提取变量失败: {str(e)}'}

    def _wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """等待"""
        duration = params.get('duration', 1)
        time.sleep(duration)
        return {'success': True, 'message': f'已等待 {duration} 秒'}

    def _set_variable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """设置变量"""
        variable_name = params.get('name') or params.get('variable_name')
        value = params.get('value')

        if not variable_name:
            return {'success': False, 'error': '缺少name参数'}

        self.set_variable(variable_name, value)
        return {
            'success': True,
            'message': f'已设置变量 {variable_name} = {value}'
        }

    def _resolve_url(self, url: str) -> str:
        """解析URL（处理变量）"""
        url = self._resolve_variables(url)
        if url and not url.startswith('http'):
            return self.base_url.rstrip('/') + '/' + url.lstrip('/')
        return url

    def _resolve_variables(self, data: Any) -> Any:
        """递归解析变量"""
        # 使用父类的resolve_variables方法
        return self.resolve_variables(data)

    def _get_json_value(self, data: Any, path: str) -> Any:
        """通过JSONPath获取值"""
        keys = path.split('.')
        current = data

        for key in keys:
            # 处理数组索引 [0]
            if '[' in key:
                name, index = key.split('[')
                if name:
                    current = current.get(name)
                index = int(index.rstrip(']'))
                if isinstance(current, list):
                    current = current[index]
            else:
                if isinstance(current, dict):
                    current = current.get(key)
                else:
                    return None

        return current

    def _execute_script(self, script: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行前置/后置脚本

        参数:
            script: Python代码字符串
            context: 脚本上下文变量

        返回:
            执行结果
        """
        try:
            # 准备脚本执行环境
            script_context = {
                'variables': self.variables,
                'set_variable': self.set_variable,
                'get_variable': self.get_variable,
                '__builtins__': {}
            }

            if context:
                script_context.update(context)

            # 执行脚本
            exec(script, script_context)

            return {'success': True, 'message': '脚本执行成功'}

        except Exception as e:
            return {
                'success': False,
                'error': f'脚本执行失败: {str(e)}'
            }

    def _apply_signing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用请求签名或加密

        支持的算法:
        - MD5
        - SHA256
        - HMAC-SHA256
        - AES
        - RSA

        参数:
            params: 请求参数，包含:
                - sign_type: 签名类型
                - sign_algorithm: 签名算法
                - sign_key: 签名密钥
                - sign_position: 签名位置 (header, query, body)
                - sign_field: 签名字段名

        返回:
            包含签名后headers或body的字典
        """
        sign_type = params.get('sign_type', 'hash')
        sign_algorithm = params.get('sign_algorithm', 'MD5').lower()
        sign_key = params.get('sign_key', '')
        sign_position = params.get('sign_position', 'header')
        sign_field = params.get('sign_field', 'sign')

        result = {}

        try:
            # 构建待签名字符串
            if sign_position == 'header':
                data_to_sign = str(params.get('headers', {}))
            elif sign_position == 'query':
                data_to_sign = str(params.get('params', {}))
            else:  # body
                data_to_sign = str(params.get('body', ''))

            # 添加密钥
            if sign_key:
                data_to_sign += sign_key

            # 计算签名
            import hashlib
            import hmac

            if sign_algorithm == 'md5':
                sign_value = hashlib.md5(data_to_sign.encode('utf-8')).hexdigest()
            elif sign_algorithm == 'sha256':
                sign_value = hashlib.sha256(data_to_sign.encode('utf-8')).hexdigest()
            elif sign_algorithm == 'hmac-sha256':
                sign_value = hmac.new(
                    sign_key.encode('utf-8'),
                    data_to_sign.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
            else:
                return {'success': False, 'error': f'不支持的签名算法: {sign_algorithm}'}

            # 根据位置添加签名
            if sign_position == 'header':
                result['headers'] = {sign_field: sign_value}
            elif sign_position == 'query':
                params_dict = params.get('params', {})
                params_dict[sign_field] = sign_value
                result['params'] = params_dict
            else:  # body
                body = params.get('body', {})
                if isinstance(body, dict):
                    body[sign_field] = sign_value
                    result['body'] = body

            result['success'] = True
            result['sign_value'] = sign_value

            return result

        except Exception as e:
            return {
                'success': False,
                'error': f'签名处理失败: {str(e)}'
            }
