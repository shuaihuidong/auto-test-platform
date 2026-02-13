"""
Playwright测试引擎实现
"""
import asyncio
import time
import os
from typing import Dict, Any
from django.conf import settings

from .base import TestEngine


class PlaywrightEngine(TestEngine):
    """
    Playwright测试引擎
    支持Chromium、Firefox和WebKit浏览器
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.browser_type = self.config.get('browser', 'chromium')
        self.headless = self.config.get('headless', False)
        self.timeout = self.config.get('timeout', 10000)  # Playwright uses milliseconds
        self.screenshot_dir = settings.SCREENSHOTS_ROOT
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def setup(self) -> bool:
        """初始化Playwright"""
        try:
            from playwright.sync_api import sync_playwright

            self.playwright = sync_playwright().start()

            if self.browser_type == 'chromium':
                browser_launcher = self.playwright.chromium
            elif self.browser_type == 'firefox':
                browser_launcher = self.playwright.firefox
            elif self.browser_type == 'webkit':
                browser_launcher = self.playwright.webkit
            else:
                raise ValueError(f"不支持的浏览器: {self.browser_type}")

            self.browser = browser_launcher.launch(headless=self.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.page.set_default_timeout(self.timeout)

            self.add_log(f"Playwright {self.browser_type} 初始化成功")
            return True

        except Exception as e:
            self.add_log(f"Playwright初始化失败: {str(e)}", 'error')
            return False

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """执行Playwright测试步骤"""
        start_time = time.time()
        step_type = step.get('type')
        params = step.get('params', {})

        try:
            if step_type == 'goto':
                result = self._goto(params)
            elif step_type == 'click':
                result = self._click(params)
            elif step_type == 'input':
                result = self._input(params)
            elif step_type == 'assert':
                result = self._assert(params)
            elif step_type == 'wait':
                result = self._wait(params)
            elif step_type == 'scroll':
                result = self._scroll(params)
            elif step_type == 'switch':
                result = self._switch(params)
            elif step_type == 'execute_script':
                result = self._execute_script(params)
            elif step_type == 'screenshot':
                result = self._screenshot(params)
            elif step_type == 'hover':
                result = self._hover(params)
            elif step_type == 'select':
                result = self._select(params)
            elif step_type == 'upload':
                result = self._upload(params)
            elif step_type == 'set_variable':
                result = self._set_variable(params)
            elif step_type == 'extract_variable':
                result = self._extract_variable(params)
            else:
                result = {
                    'success': False,
                    'error': f'未知的步骤类型: {step_type}'
                }

            result['duration'] = round((time.time() - start_time) * 1000, 2)

            # 如果步骤失败，尝试截图
            if not result.get('success') and self.config.get('screenshot_on_failure', True):
                screenshot_path = self._take_screenshot(f"step_{self.current_step_index}_failure")
                if screenshot_path:
                    result['screenshot'] = screenshot_path

            return result

        except Exception as e:
            return {
                'success': False,
                'error': f'步骤执行异常: {str(e)}',
                'duration': round((time.time() - start_time) * 1000, 2)
            }

    def teardown(self) -> None:
        """清理Playwright资源"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.add_log("Playwright已关闭")
        except Exception as e:
            self.add_log(f"关闭Playwright时出错: {str(e)}", 'error')

    def get_result(self) -> Dict[str, Any]:
        """获取测试结果"""
        return self.results

    def _find_element(self, locator: Dict[str, Any]):
        """查找页面元素"""
        locator_type = locator.get('type', 'xpath')
        value = locator.get('value', '')

        # 验证 value 不为空
        if not value or not value.strip():
            raise ValueError(f"定位器值不能为空 (type: {locator_type})")

        if locator_type == 'xpath':
            return self.page.locator(f'xpath={value}')
        elif locator_type == 'css':
            return self.page.locator(f'css={value}')
        elif locator_type == 'id':
            return self.page.locator(f'#{value}')
        elif locator_type == 'text':
            return self.page.get_by_text(value)
        elif locator_type == 'label':
            return self.page.get_by_label(value)
        elif locator_type == 'placeholder':
            return self.page.get_by_placeholder(value)
        elif locator_type == 'role':
            # value format: "button[name='Submit']"
            return self.page.get_by_role(value.split('[')[0], **self._parse_role_params(value))
        else:
            return self.page.locator(value)

    def _parse_role_params(self, role_value: str) -> Dict[str, str]:
        """解析role参数"""
        import re
        params = {}
        # 提取方括号中的参数
        match = re.search(r'\[(.*?)\]', role_value)
        if match:
            param_str = match.group(1)
            # 解析 key='value' 格式
            for m in re.finditer(r"(\w+)='([^']*)'", param_str):
                params[m.group(1)] = m.group(2)
        return params

    def _goto(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """导航到指定URL"""
        url = params.get('url')
        if not url:
            return {'success': False, 'error': '缺少url参数'}

        wait_until = params.get('wait_until', 'load')
        self.page.goto(url, wait_until=wait_until)
        return {'success': True, 'message': f'已导航到 {url}'}

    def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """点击元素"""
        locator = params.get('locator')
        if not locator:
            return {'success': False, 'error': '缺少locator参数'}

        element = self._find_element(locator)
        element.click(timeout=params.get('timeout', self.timeout))
        return {'success': True, 'message': '已点击元素'}

    def _input(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """输入文本"""
        locator = params.get('locator')
        value = params.get('value')
        clear_first = params.get('clear_first', True)

        if not locator or value is None:
            return {'success': False, 'error': '缺少locator或value参数'}

        element = self._find_element(locator)
        if clear_first:
            element.fill('')
        element.fill(str(value))
        return {'success': True, 'message': f'已输入文本: {value}'}

    def _assert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """断言"""
        assert_type = params.get('assert_type', 'text')
        locator = params.get('locator')
        expected = params.get('expected')

        try:
            if assert_type == 'text':
                element = self._find_element(locator) if locator else self.page
                actual = element.inner_text() if locator else self.page.inner_text()
                success = str(actual).strip() == str(expected).strip()
                return {
                    'success': success,
                    'message': f'文本断言: 期望="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'exists':
                element = self._find_element(locator)
                element.count() > 0
                return {'success': True, 'message': '元素存在'}

            elif assert_type == 'visible':
                element = self._find_element(locator)
                is_visible = element.is_visible()
                return {
                    'success': is_visible,
                    'message': f'元素可见性: {is_visible}'
                }

            elif assert_type == 'attribute':
                attr_name = params.get('attribute', 'value')
                element = self._find_element(locator)
                actual = element.get_attribute(attr_name)
                success = str(actual) == str(expected)
                return {
                    'success': success,
                    'message': f'属性断言 [{attr_name}]: 期望="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'url':
                actual = self.page.url
                success = actual == expected or actual.startswith(expected)
                return {
                    'success': success,
                    'message': f'URL断言: 期望="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'title':
                actual = self.page.title()
                success = str(actual) == str(expected)
                return {
                    'success': success,
                    'message': f'标题断言: 期望="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'count':
                element = self._find_element(locator)
                actual = element.count()
                expected_count = int(expected)
                success = actual == expected_count
                return {
                    'success': success,
                    'message': f'数量断言: 期望={expected_count}, 实际={actual}',
                    'expected': expected_count,
                    'actual': actual
                }

            elif assert_type == 'contains':
                element = self._find_element(locator) if locator else self.page
                actual = element.inner_text() if locator else self.page.inner_text()
                success = str(expected) in str(actual)
                return {
                    'success': success,
                    'message': f'文本包含断言: 期望包含="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'not_contains':
                element = self._find_element(locator) if locator else self.page
                actual = element.inner_text() if locator else self.page.inner_text()
                success = str(expected) not in str(actual)
                return {
                    'success': success,
                    'message': f'文本不包含断言: 期望不包含="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'regex':
                import re
                element = self._find_element(locator) if locator else self.page
                actual = element.inner_text() if locator else self.page.inner_text()
                try:
                    pattern = re.compile(str(expected))
                    success = pattern.search(str(actual)) is not None
                    return {
                        'success': success,
                        'message': f'正则匹配断言: pattern="{expected}", 实际="{actual}"',
                        'expected': expected,
                        'actual': actual
                    }
                except re.error as e:
                    return {'success': False, 'error': f'正则表达式错误: {str(e)}'}

            elif assert_type == 'numeric_compare':
                element = self._find_element(locator) if locator else self.page
                actual = element.inner_text() if locator else self.page.inner_text()
                operator = params.get('operator', '==')

                try:
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
                        'message': f'数值比较断言: 期望 {operator} {expected_num}, 实际={actual_num}',
                        'expected': expected_num,
                        'actual': actual_num
                    }
                except (ValueError, TypeError):
                    return {'success': False, 'error': '无法转换为数值进行比较'}

            elif assert_type == 'page_contains':
                text = params.get('text', expected)
                page_content = self.page.content()
                success = str(text) in page_content
                return {
                    'success': success,
                    'message': f'页面包含断言: 期望页面包含="{text}", 结果={success}',
                    'expected': text,
                    'actual': 'found' if success else 'not found'
                }

            else:
                return {'success': False, 'error': f'未知的断言类型: {assert_type}'}

        except Exception as e:
            return {'success': False, 'error': f'断言失败: {str(e)}'}

    def _wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """等待"""
        wait_type = params.get('wait_type', 'fixed')
        duration = params.get('duration', 1000)

        if wait_type == 'fixed':
            self.page.wait_for_timeout(duration)
            return {'success': True, 'message': f'已等待 {duration} ms'}

        elif wait_type == 'selector':
            locator = params.get('locator')
            if not locator:
                return {'success': False, 'error': '缺少locator参数'}

            element = self._find_element(locator)
            state = params.get('state', 'visible')
            element.wait_for(state=state, timeout=duration)
            return {'success': True, 'message': f'元素已{state}'}

        elif wait_type == 'navigation':
            self.page.wait_for_load_state(state=params.get('state', 'load'), timeout=duration)
            return {'success': True, 'message': '导航已完成'}

        elif wait_type == 'url':
            expected_url = params.get('url')
            self.page.wait_for_url(expected_url, timeout=duration)
            return {'success': True, 'message': f'已跳转到 {expected_url}'}

        return {'success': False, 'error': f'未知的等待类型: {wait_type}'}

    def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """滚动页面"""
        scroll_type = params.get('scroll_type', 'position')

        if scroll_type == 'position':
            x = params.get('x', 0)
            y = params.get('y', 0)
            self.page.evaluate(f'window.scrollTo({x}, {y})')
            return {'success': True, 'message': f'已滚动到 ({x}, {y})'}

        elif scroll_type == 'element':
            locator = params.get('locator')
            if not locator:
                return {'success': False, 'error': '缺少locator参数'}

            element = self._find_element(locator)
            element.scroll_into_view_if_needed()
            return {'success': True, 'message': '已滚动到元素'}

        elif scroll_type == 'bottom':
            self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            return {'success': True, 'message': '已滚动到底部'}

        return {'success': False, 'error': f'未知的滚动类型: {scroll_type}'}

    def _switch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """切换上下文"""
        switch_type = params.get('switch_type', 'page')

        if switch_type == 'page':
            # Playwright中每个page都是独立的
            page_index = params.get('index', -1)
            if page_index >= 0:
                pages = self.context.pages
                if page_index < len(pages):
                    self.page = pages[page_index]
                    return {'success': True, 'message': f'已切换到页面 {page_index}'}

            # 切换到最新打开的页面
            if self.context.pages:
                self.page = self.context.pages[-1]
                return {'success': True, 'message': '已切换到最新页面'}

        elif switch_type == 'frame':
            locator = params.get('locator')
            if locator:
                element = self._find_element(locator)
                frame_name = element.get_attribute('name')
                self.page.frame(name=frame_name)
            else:
                # 切换回主文档
                pass
            return {'success': True, 'message': '已切换框架'}

        return {'success': False, 'error': f'未知的切换类型: {switch_type}'}

    def _execute_script(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行JavaScript"""
        script = params.get('script')
        if not script:
            return {'success': False, 'error': '缺少script参数'}

        result = self.page.evaluate(script)
        return {
            'success': True,
            'message': '已执行JavaScript',
            'result': result
        }

    def _screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """截图"""
        filename = params.get('filename', f'step_{self.current_step_index}')
        full_page = params.get('full_page', False)
        path = self._take_screenshot(filename, full_page)
        if path:
            return {'success': True, 'message': f'已截图: {path}', 'screenshot': path}
        return {'success': False, 'error': '截图失败'}

    def _take_screenshot(self, filename: str, full_page: bool = False) -> str:
        """实际执行截图"""
        try:
            os.makedirs(self.screenshot_dir, exist_ok=True)
            filepath = os.path.join(self.screenshot_dir, f'{filename}.png')
            self.page.screenshot(path=filepath, full_page=full_page)
            return filepath
        except Exception as e:
            self.add_log(f'截图失败: {str(e)}', 'error')
            return None

    def _hover(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """鼠标悬停"""
        locator = params.get('locator')
        if not locator:
            return {'success': False, 'error': '缺少locator参数'}

        element = self._find_element(locator)
        element.hover()
        return {'success': True, 'message': '已悬停'}

    def _select(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """选择下拉选项"""
        locator = params.get('locator')
        value = params.get('value')

        if not locator or value is None:
            return {'success': False, 'error': '缺少locator或value参数'}

        element = self._find_element(locator)
        element.select_option(value)
        return {'success': True, 'message': f'已选择: {value}'}

    def _upload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """上传文件"""
        locator = params.get('locator')
        file_path = params.get('file_path')

        if not locator or not file_path:
            return {'success': False, 'error': '缺少locator或file_path参数'}

        element = self._find_element(locator)
        element.set_input_files(file_path)
        return {'success': True, 'message': f'已上传文件: {file_path}'}

    def _set_variable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        设置变量

        参数:
            params: 包含:
                - name: 变量名
                - value: 变量值
        """
        name = params.get('name')
        value = params.get('value')

        if not name:
            return {'success': False, 'error': '缺少name参数'}

        self.set_variable(name, value)
        return {
            'success': True,
            'message': f'已设置变量: {name} = {value}'
        }

    def _extract_variable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        从页面元素提取变量

        参数:
            params: 包含:
                - name: 变量名
                - locator: 元素定位器
                - extract_type: 提取类型 (text, attribute, value)
                - attribute: 属性名（当extract_type为attribute时使用）
                - pattern: 提取模式（正则表达式，可选）
        """
        name = params.get('name')
        locator = params.get('locator')
        extract_type = params.get('extract_type', 'text')

        if not name:
            return {'success': False, 'error': '缺少name参数'}

        try:
            if extract_type in ['text', 'attribute', 'value']:
                if not locator:
                    return {'success': False, 'error': f'{extract_type}类型需要locator参数'}

                element = self._find_element(locator)

                if extract_type == 'text':
                    extracted_value = element.inner_text()
                elif extract_type == 'attribute':
                    attr_name = params.get('attribute', 'value')
                    extracted_value = element.get_attribute(attr_name)
                elif extract_type == 'value':
                    extracted_value = element.input_value()
                else:
                    extracted_value = None

            elif extract_type == 'url':
                extracted_value = self.page.url

            elif extract_type == 'title':
                extracted_value = self.page.title()

            elif extract_type == 'cookie':
                cookie_name = params.get('cookie_name')
                if cookie_name:
                    context_cookies = self.context.cookies()
                    extracted_value = next(
                        (c.get('value') for c in context_cookies if c.get('name') == cookie_name),
                        None
                    )
                else:
                    extracted_value = self.context.cookies()

            else:
                return {'success': False, 'error': f'未知的提取类型: {extract_type}'}

            # 如果指定了提取模式（正则表达式），则进行模式匹配提取
            pattern = params.get('pattern')
            if pattern and extracted_value:
                extracted_value = self.extract_from_text(str(extracted_value), pattern)

            if extracted_value is None:
                return {'success': False, 'error': '提取值为空'}

            self.set_variable(name, extracted_value)
            return {
                'success': True,
                'message': f'已提取变量: {name} = {extracted_value}',
                'value': extracted_value
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'提取变量失败: {str(e)}'
            }
