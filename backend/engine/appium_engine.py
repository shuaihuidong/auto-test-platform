"""
Appium测试引擎实现
"""
import time
import os
from typing import Dict, Any
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from django.conf import settings

from .base import TestEngine


class AppiumEngine(TestEngine):
    """
    Appium测试引擎
    支持Android和iOS移动应用自动化
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.platform = self.config.get('platform', 'android')  # android or ios
        self.timeout = self.config.get('timeout', 10)
        self.screenshot_dir = settings.SCREENSHOTS_ROOT
        self.appium_server = self.config.get('appium_server', 'http://localhost:4723')

    def setup(self) -> bool:
        """初始化Appium driver"""
        try:
            options = AppiumOptions()

            if self.platform == 'android':
                # Android配置
                capabilities = {
                    'platformName': 'Android',
                    'automationName': 'UiAutomator2',
                    'deviceName': self.config.get('device_name', 'Android'),
                    'appPackage': self.config.get('app_package'),
                    'appActivity': self.config.get('app_activity'),
                    'app': self.config.get('app_path'),
                    'udid': self.config.get('udid'),
                    'noReset': self.config.get('no_reset', True),
                    'fullReset': self.config.get('full_reset', False),
                    'unicodeKeyboard': True,
                    'resetKeyboard': True
                }
                options.load_capabilities(capabilities)

            elif self.platform == 'ios':
                # iOS配置
                capabilities = {
                    'platformName': 'iOS',
                    'automationName': 'XCUITest',
                    'deviceName': self.config.get('device_name', 'iPhone'),
                    'bundleId': self.config.get('bundle_id'),
                    'app': self.config.get('app_path'),
                    'udid': self.config.get('udid'),
                    'noReset': self.config.get('no_reset', True),
                    'fullReset': self.config.get('full_reset', False)
                }
                options.load_capabilities(capabilities)

            else:
                raise ValueError(f"不支持的平台: {self.platform}")

            self.driver = webdriver.Remote(self.appium_server, options=options)
            self.driver.implicitly_wait(self.timeout)

            self.add_log(f"Appium {self.platform} driver初始化成功")
            return True

        except Exception as e:
            self.add_log(f"Appium初始化失败: {str(e)}", 'error')
            return False

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """执行Appium测试步骤"""
        start_time = time.time()
        step_type = step.get('type')
        params = step.get('params', {})

        try:
            if step_type == 'click':
                result = self._click(params)
            elif step_type == 'input':
                result = self._input(params)
            elif step_type == 'assert':
                result = self._assert(params)
            elif step_type == 'wait':
                result = self._wait(params)
            elif step_type == 'swipe':
                result = self._swipe(params)
            elif step_type == 'scroll':
                result = self._scroll(params)
            elif step_type == 'screenshot':
                result = self._screenshot(params)
            elif step_type == 'tap':
                result = self._tap(params)
            elif step_type == 'press_keycode':
                result = self._press_keycode(params)
            elif step_type == 'switch_context':
                result = self._switch_context(params)
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
        """清理Appium资源"""
        if self.driver:
            try:
                self.driver.quit()
                self.add_log("Appium driver已关闭")
            except Exception as e:
                self.add_log(f"关闭driver时出错: {str(e)}", 'error')

    def get_result(self) -> Dict[str, Any]:
        """获取测试结果"""
        return self.results

    def _find_element(self, locator: Dict[str, str]):
        """查找移动元素"""
        locator_type = locator.get('type', 'id')
        value = locator.get('value', '')

        if locator_type == 'id':
            by = AppiumBy.ID
        elif locator_type == 'xpath':
            by = AppiumBy.XPATH
        elif locator_type == 'class':
            by = AppiumBy.CLASS_NAME
        elif locator_type == 'name':
            by = AppiumBy.NAME
        elif locator_type == 'accessibility_id':
            by = AppiumBy.ACCESSIBILITY_ID
        elif locator_type == 'android_uiautomator':
            by = AppiumBy.ANDROID_UIAUTOMATOR
        elif locator_type == 'ios_predicate':
            by = AppiumBy.IOS_PREDICATE
        elif locator_type == 'ios_class_chain':
            by = AppiumBy.IOS_CLASS_CHAIN
        else:
            by = AppiumBy.ID

        wait = WebDriverWait(self.driver, self.timeout)
        return wait.until(lambda driver: driver.find_element(by, value))

    def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """点击元素"""
        locator = params.get('locator')
        if not locator:
            return {'success': False, 'error': '缺少locator参数'}

        element = self._find_element(locator)
        element.click()
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
            element.clear()
        element.send_keys(str(value))
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
                return {'success': True, 'message': '元素存在'}

            elif assert_type == 'enabled':
                element = self._find_element(locator)
                is_enabled = element.is_enabled()
                return {
                    'success': is_enabled,
                    'message': f'元素可用: {is_enabled}'
                }

            elif assert_type == 'displayed':
                element = self._find_element(locator)
                is_displayed = element.is_displayed()
                return {
                    'success': is_displayed,
                    'message': f'元素可见: {is_displayed}'
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

            self._find_element(locator)
            return {'success': True, 'message': '元素已出现'}

        return {'success': False, 'error': f'未知的等待类型: {wait_type}'}

    def _swipe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """滑动"""
        start_x = params.get('start_x', 500)
        start_y = params.get('start_y', 500)
        end_x = params.get('end_x', 500)
        end_y = params.get('end_y', 100)
        duration = params.get('duration', 500)

        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        return {
            'success': True,
            'message': f'已从 ({start_x}, {start_y}) 滑动到 ({end_x}, {end_y})'
        }

    def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """滚动到元素"""
        locator = params.get('locator')
        if not locator:
            return {'success': False, 'error': '缺少locator参数'}

        element = self._find_element(locator)

        if self.platform == 'android':
            self.driver.execute_script('mobile: scroll', {
                'elementId': element.id,
                'strategy': locator.get('type', 'id'),
                'selector': locator.get('value', '')
            })
        else:
            element.location_once_scrolled_into_view

        return {'success': True, 'message': '已滚动到元素'}

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

    def _tap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """点击坐标"""
        x = params.get('x', 0)
        y = params.get('y', 0)

        if self.platform == 'android':
            self.driver.execute_script('mobile: tap', {
                'x': x,
                'y': y
            })
        else:
            self.driver.execute_script('mobile: tap', {
                'x': x,
                'y': y
            })

        return {'success': True, 'message': f'已点击坐标 ({x}, {y})'}

    def _press_keycode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """按键"""
        keycode = params.get('keycode')
        if keycode is None:
            return {'success': False, 'error': '缺少keycode参数'}

        if self.platform == 'android':
            self.driver.press_keycode(int(keycode))
        else:
            # iOS使用不同的方法
            pass

        return {'success': True, 'message': f'已按键: {keycode}'}

    def _switch_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """切换上下文（用于混合应用）"""
        context_type = params.get('context_type', 'native')

        if context_type == 'webview':
            # 切换到WebView
            contexts = self.driver.contexts
            webview_context = [c for c in contexts if 'WEBVIEW' in c]
            if webview_context:
                self.driver.switch_to.context(webview_context[0])
                return {'success': True, 'message': f'已切换到WebView: {webview_context[0]}'}

        elif context_type == 'native':
            # 切换回原生
            self.driver.switch_to.context('NATIVE_APP')
            return {'success': True, 'message': '已切换到原生应用'}

        return {'success': False, 'error': '无法切换上下文'}
