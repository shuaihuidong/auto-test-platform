"""
Selenium测试引擎实现
"""
import time
import os
import urllib.request
from typing import Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from django.conf import settings

from .base import TestEngine


class SeleniumEngine(TestEngine):
    """
    Selenium测试引擎
    支持Chrome和Firefox浏览器
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.browser = self.config.get('browser', 'chrome')
        self.headless = self.config.get('headless', False)
        self.timeout = self.config.get('timeout', 10)
        self.screenshot_dir = settings.SCREENSHOTS_ROOT

    def setup(self) -> bool:
        """初始化Selenium WebDriver"""
        try:
            if self.browser == 'chrome':
                options = ChromeOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')

                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)

            elif self.browser == 'firefox':
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument('--headless')

                from webdriver_manager.firefox import GeckoDriverManager
                from selenium.webdriver.firefox.service import Service
                service = Service(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)

            else:
                raise ValueError(f"不支持的浏览器: {self.browser}")

            self.driver.implicitly_wait(self.timeout)
            self.add_log(f"Selenium {self.browser} driver初始化成功")
            return True

        except Exception as e:
            self.add_log(f"Selenium初始化失败: {str(e)}", 'error')
            return False

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """执行Selenium测试步骤"""
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
            elif step_type == 'module':
                # 模块步骤需要递归执行子步骤
                result = self._execute_module(params)
            elif step_type == 'set_variable':
                result = self._set_variable(params)
            elif step_type == 'extract_variable':
                result = self._extract_variable(params)
            elif step_type == 'upload':
                result = self._execute_upload(params)
            elif step_type == 'download':
                result = self._execute_download(params)
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
        """清理WebDriver资源"""
        if self.driver:
            try:
                self.driver.quit()
                self.add_log("WebDriver已关闭")
            except Exception as e:
                self.add_log(f"关闭WebDriver时出错: {str(e)}", 'error')

    def get_result(self) -> Dict[str, Any]:
        """获取测试结果"""
        return self.results

    def _find_element(self, locator: Dict[str, str]):
        """查找页面元素"""
        by_type = self._get_by_type(locator.get('type', 'xpath'))
        value = locator.get('value', '')

        wait = WebDriverWait(self.driver, self.timeout)
        return wait.until(EC.presence_of_element_located((by_type, value)))

    def _get_by_type(self, locator_type: str):
        """获取By定位类型"""
        mapping = {
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME,
            'xpath': By.XPATH,
            'css': By.CSS_SELECTOR,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT
        }
        return mapping.get(locator_type, By.XPATH)

    def _goto(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """导航到指定URL"""
        url = params.get('url')
        if not url:
            return {'success': False, 'error': '缺少url参数'}

        self.driver.get(url)
        return {'success': True, 'message': f'已导航到 {url}'}

    def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """点击元素"""
        locator = params.get('locator')
        if not locator:
            return {'success': False, 'error': '缺少locator参数'}

        element = self._find_element(locator)
        element.click()
        return {'success': True, 'message': f'已点击元素'}

    def _input(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """输入文本"""
        locator = params.get('locator')
        value = params.get('value')
        clear_first = params.get('clear_first', True)

        if not locator or value is None:
            return {'success': False, 'error': '缺少locator或value参数'}

        element = self._find_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(value)
        return {'success': True, 'message': f'已输入文本: {value}'}

    def _assert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """断言"""
        assert_type = params.get('assert_type', 'text')
        locator = params.get('locator')
        expected = params.get('expected')

        try:
            if assert_type == 'text':
                element = self._find_element(locator)
                actual = element.text
                success = str(actual) == str(expected)
                return {
                    'success': success,
                    'message': f'文本断言: 期望="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'exists':
                element = self._find_element(locator)
                return {
                    'success': True,
                    'message': '元素存在'
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
                actual = self.driver.current_url
                success = actual == expected or actual.startswith(expected)
                return {
                    'success': success,
                    'message': f'URL断言: 期望="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'title':
                actual = self.driver.title
                success = str(actual) == str(expected)
                return {
                    'success': success,
                    'message': f'标题断言: 期望="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'contains':
                element = self._find_element(locator)
                actual = element.text
                success = str(expected) in str(actual)
                return {
                    'success': success,
                    'message': f'文本包含断言: 期望包含="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'not_contains':
                element = self._find_element(locator)
                actual = element.text
                success = str(expected) not in str(actual)
                return {
                    'success': success,
                    'message': f'文本不包含断言: 期望不包含="{expected}", 实际="{actual}"',
                    'expected': expected,
                    'actual': actual
                }

            elif assert_type == 'regex':
                import re
                element = self._find_element(locator)
                actual = element.text
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
                element = self._find_element(locator)
                actual = element.text
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
                page_source = self.driver.page_source
                success = str(text) in page_source
                return {
                    'success': success,
                    'message': f'页面包含断言: 期望页面包含="{text}", 结果={success}',
                    'expected': text,
                    'actual': 'found' if success else 'not found'
                }

            else:
                return {'success': False, 'error': f'未知的断言类型: {assert_type}'}

        except TimeoutException:
            return {'success': False, 'error': '元素定位超时'}

    def _wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """等待"""
        wait_type = params.get('wait_type', 'fixed')
        duration = params.get('duration', 1)

        if wait_type == 'fixed':
            time.sleep(duration)
            return {'success': True, 'message': f'已等待 {duration} 秒'}

        elif wait_type == 'element':
            locator = params.get('locator')
            if not locator:
                return {'success': False, 'error': '缺少locator参数'}

            by_type = self._get_by_type(locator.get('type', 'xpath'))
            value = locator.get('value')
            WebDriverWait(self.driver, duration).until(
                EC.presence_of_element_located((by_type, value))
            )
            return {'success': True, 'message': f'元素已出现'}

        return {'success': False, 'error': f'未知的等待类型: {wait_type}'}

    def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """滚动页面"""
        scroll_type = params.get('scroll_type', 'position')
        x = params.get('x', 0)
        y = params.get('y', 0)

        if scroll_type == 'position':
            self.driver.execute_script(f'window.scrollTo({x}, {y});')
            return {'success': True, 'message': f'已滚动到 ({x}, {y})'}

        elif scroll_type == 'element':
            locator = params.get('locator')
            if not locator:
                return {'success': False, 'error': '缺少locator参数'}

            element = self._find_element(locator)
            self.driver.execute_script('arguments[0].scrollIntoView(true);', element)
            return {'success': True, 'message': '已滚动到元素'}

        elif scroll_type == 'bottom':
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            return {'success': True, 'message': '已滚动到底部'}

        return {'success': False, 'error': f'未知的滚动类型: {scroll_type}'}

    def _switch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """切换上下文"""
        switch_type = params.get('switch_type', 'window')

        if switch_type == 'window':
            handle = params.get('handle')
            if handle:
                self.driver.switch_to.window(handle)
            else:
                # 切换到最新窗口
                self.driver.switch_to.window(self.driver.window_handles[-1])
            return {'success': True, 'message': '已切换窗口'}

        elif switch_type == 'frame':
            locator = params.get('locator')
            if locator:
                element = self._find_element(locator)
                self.driver.switch_to.frame(element)
            else:
                self.driver.switch_to.default_content()
            return {'success': True, 'message': '已切换框架'}

        elif switch_type == 'alert':
            alert = self.driver.switch_to.alert
            action = params.get('action', 'accept')
            if action == 'accept':
                alert.accept()
            else:
                alert.dismiss()
            return {'success': True, 'message': f'已{action}弹窗'}

        return {'success': False, 'error': f'未知的切换类型: {switch_type}'}

    def _execute_script(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行JavaScript"""
        script = params.get('script')
        if not script:
            return {'success': False, 'error': '缺少script参数'}

        result = self.driver.execute_script(script)
        return {
            'success': True,
            'message': '已执行JavaScript',
            'result': result
        }

    def _screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """截图"""
        filename = params.get('filename', f'step_{self.current_step_index}')
        path = self._take_screenshot(filename)
        if path:
            return {'success': True, 'message': f'已截图: {path}', 'screenshot': path}
        return {'success': False, 'error': '截图失败'}

    def _take_screenshot(self, filename: str) -> str:
        """实际执行截图"""
        try:
            os.makedirs(self.screenshot_dir, exist_ok=True)
            filepath = os.path.join(self.screenshot_dir, f'{filename}.png')
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            self.add_log(f'截图失败: {str(e)}', 'error')
            return None

    def _execute_module(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行模块（子步骤）"""
        # 模块执行需要在外部处理，这里只是占位
        # 实际实现中，模块应该被展开为具体步骤
        return {
            'success': False,
            'error': '模块步骤需要在外部展开执行'
        }

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
                    extracted_value = element.text
                elif extract_type == 'attribute':
                    attr_name = params.get('attribute', 'value')
                    extracted_value = element.get_attribute(attr_name)
                elif extract_type == 'value':
                    extracted_value = element.get_attribute('value')
                else:
                    extracted_value = None

            elif extract_type == 'url':
                extracted_value = self.driver.current_url

            elif extract_type == 'title':
                extracted_value = self.driver.title

            elif extract_type == 'cookie':
                cookie_name = params.get('cookie_name')
                if cookie_name:
                    cookie = self.driver.get_cookie(cookie_name)
                    extracted_value = cookie.get('value') if cookie else None
                else:
                    extracted_value = self.driver.get_cookies()

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

    def _execute_upload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文件上传

        参数:
            params: 包含:
                - locator: 文件输入元素定位器
                - file_path: 要上传的文件路径（支持变量替换）
        """
        locator = params.get('locator')
        file_path = params.get('file_path')

        if not locator:
            return {'success': False, 'error': '缺少locator参数'}
        if not file_path:
            return {'success': False, 'error': '缺少file_path参数'}

        try:
            # 查找文件输入元素
            element = self._find_element(locator)

            # 解析文件路径中的变量
            resolved_path = self.resolve_variables(file_path)

            # 检查文件是否存在
            if not os.path.exists(resolved_path):
                return {'success': False, 'error': f'文件不存在: {resolved_path}'}

            # 使用 send_keys 上传文件
            element.send_keys(resolved_path)

            return {
                'success': True,
                'message': f'已上传文件: {resolved_path}'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'文件上传失败: {str(e)}'
            }

    def _execute_download(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文件下载

        参数:
            params: 包含:
                - url: 下载链接URL（可选，如果不提供则使用当前页面）
                - save_path: 保存路径（可选，默认使用下载目录）
                - wait_time: 等待下载完成的秒数（可选，默认5秒）
        """
        url = params.get('url')
        save_path = params.get('save_path', '')
        wait_time = params.get('wait_time', 5)

        try:
            # 如果提供了URL，先导航到该URL
            if url:
                resolved_url = self.resolve_variables(url)
                self.driver.get(resolved_url)
            else:
                resolved_url = self.driver.current_url

            # 如果没有指定保存路径，使用默认下载目录
            if not save_path:
                # 使用媒体根目录下的 downloads 文件夹
                download_dir = getattr(settings, 'DOWNLOADS_ROOT', os.path.join(settings.MEDIA_ROOT, 'downloads'))
                os.makedirs(download_dir, exist_ok=True)

                # 从URL中提取文件名
                filename = os.path.basename(resolved_url) or f'download_{int(time.time())}'
                save_path = os.path.join(download_dir, filename)
            else:
                # 解析保存路径中的变量
                save_path = self.resolve_variables(save_path)

            # 等待下载完成
            time.sleep(wait_time)

            # 这里需要根据实际情况处理下载逻辑
            # 对于简单的下载链接，可以使用 urllib 直接下载
            if url:
                urllib.request.urlretrieve(resolved_url, save_path)
                return {
                    'success': True,
                    'message': f'文件已下载到: {save_path}',
                    'file_path': save_path
                }
            else:
                # 对于需要浏览器交互的下载（如点击按钮后触发下载）
                # 需要配置浏览器的下载目录偏好
                # 这里简化处理，实际应用中需要更复杂的逻辑
                return {
                    'success': True,
                    'message': '下载已触发（请检查浏览器下载目录）'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'文件下载失败: {str(e)}'
            }
