"""
Selenium 执行引擎 - 执行测试脚本
- 支持多种浏览器 (Chrome/Firefox/Edge)
- 解析脚本步骤并执行
- 截图、日志记录
- 变量替换
"""

import base64
import time
from io import BytesIO
from typing import Dict, Any, Optional, List
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException, TimeoutException

from config import get_config_manager


class StepExecutor:
    """
    单个步骤执行器

    负责执行单个测试步骤
    """

    def __init__(self, driver: webdriver.Remote):
        """
        初始化步骤执行器

        Args:
            driver: Selenium WebDriver 实例
        """
        self.driver = driver

    def execute(self, step: Dict[str, Any], variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行一个步骤

        Args:
            step: 步骤定义 {type: str, name: str, params: dict}
            variables: 变量字典，用于替换 ${变量名}

        Returns:
            执行结果 {success: bool, message: str, screenshot: str}
        """
        step_type = step.get("type")
        step_name = step.get("name", "")
        params = step.get("params", {})

        # 替换变量
        params = self._replace_variables(params, variables or {})

        logger.info(f"执行步骤: {step_name} (类型: {step_type})")

        try:
            # 根据步骤类型分发到不同的执行方法
            result = self._execute_by_type(step_type, params)

            if result["success"]:
                logger.info(f"步骤执行成功: {step_name}")
            else:
                logger.error(f"步骤执行失败: {step_name} - {result['message']}")

            return result

        except Exception as e:
            logger.exception(f"步骤执行异常: {step_name}")
            return {
                "success": False,
                "message": f"执行异常: {str(e)}",
                "screenshot": self._capture_screenshot()
            }

    def _replace_variables(self, params: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        替换参数中的变量

        Args:
            params: 原始参数
            variables: 变量字典

        Returns:
            替换后的参数
        """
        import json

        def replace_value(value: Any) -> Any:
            """递归替换值中的变量"""
            if isinstance(value, str):
                # 替换 ${变量名} 格式的变量
                for var_name, var_value in variables.items():
                    value = value.replace(f"${{{var_name}}}", str(var_value))
                return value
            elif isinstance(value, dict):
                return {k: replace_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_value(v) for v in value]
            else:
                return value

        return replace_value(params)

    def _execute_by_type(self, step_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据步骤类型执行

        Args:
            step_type: 步骤类型
            params: 步骤参数

        Returns:
            执行结果
        """
        # 导航类步骤
        if step_type == "goto":
            return self._goto(params)
        elif step_type == "refresh":
            return self._refresh()
        elif step_type == "back":
            return self._back()
        elif step_type == "forward":
            return self._forward()

        # 交互类步骤
        elif step_type == "click":
            return self._click(params)
        elif step_type == "double_click":
            return self._double_click(params)
        elif step_type == "right_click":
            return self._right_click(params)
        elif step_type == "hover":
            return self._hover(params)
        elif step_type == "input":
            return self._input(params)
        elif step_type == "clear":
            return self._clear(params)
        elif step_type == "select":
            return self._select(params)
        elif step_type == "checkbox":
            return self._checkbox(params)

        # 断言类步骤
        elif step_type == "assert_text":
            return self._assert_text(params)
        elif step_type == "assert_title":
            return self._assert_title(params)
        elif step_type == "assert_url":
            return self._assert_url(params)
        elif step_type == "assert_element":
            return self._assert_element(params)
        elif step_type == "assert_visible":
            return self._assert_visible(params)

        # 等待类步骤
        elif step_type == "wait":
            return self._wait(params)
        elif step_type == "wait_element":
            return self._wait_element(params)

        # 截图
        elif step_type == "screenshot":
            return self._screenshot(params)

        # 滚动
        elif step_type == "scroll":
            return self._scroll(params)

        # 文件操作
        elif step_type == "upload":
            return self._upload(params)
        elif step_type == "download":
            return self._download(params)

        else:
            return {"success": False, "message": f"未知步骤类型: {step_type}"}

    # ==================== 导航方法 ====================

    def _goto(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """打开页面"""
        url = params.get("url", "")
        # 自动添加协议前缀（如果缺失）
        if url and not url.startswith(('http://', 'https://', 'file://')):
            url = 'http://' + url
        self.driver.get(url)
        return {"success": True, "message": f"打开页面: {url}"}

    def _refresh(self) -> Dict[str, Any]:
        """刷新页面"""
        self.driver.refresh()
        return {"success": True, "message": "页面已刷新"}

    def _back(self) -> Dict[str, Any]:
        """后退"""
        self.driver.back()
        return {"success": True, "message": "已后退"}

    def _forward(self) -> Dict[str, Any]:
        """前进"""
        self.driver.forward()
        return {"success": True, "message": "已前进"}

    # ==================== 交互方法 ====================

    def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """点击元素"""
        element = self._find_element(params.get("locator"))
        if element:
            element.click()
            return {"success": True, "message": "元素已点击"}
        return {"success": False, "message": "未找到元素"}

    def _double_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """双击元素"""
        element = self._find_element(params.get("locator"))
        if element:
            ActionChains(self.driver).double_click(element).perform()
            return {"success": True, "message": "元素已双击"}
        return {"success": False, "message": "未找到元素"}

    def _right_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """右键点击元素"""
        element = self._find_element(params.get("locator"))
        if element:
            ActionChains(self.driver).context_click(element).perform()
            return {"success": True, "message": "元素已右键点击"}
        return {"success": False, "message": "未找到元素"}

    def _hover(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """鼠标悬停"""
        element = self._find_element(params.get("locator"))
        if element:
            ActionChains(self.driver).move_to_element(element).perform()
            return {"success": True, "message": "鼠标已悬停"}
        return {"success": False, "message": "未找到元素"}

    def _input(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """输入文本"""
        element = self._find_element(params.get("locator"))
        if element:
            try:
                # 先点击元素，确保获得焦点
                element.click()

                # 先清空（如果配置）
                if params.get("clear_first", True):
                    try:
                        element.clear()
                    except Exception as e:
                        # 清空失败不是致命错误，继续尝试输入
                        pass

                # 输入文本
                value = params.get("value", "")
                element.send_keys(value)
                return {"success": True, "message": f"已输入: {value}"}
            except Exception as e:
                return {"success": False, "message": f"输入失败: {str(e)}"}
        return {"success": False, "message": "未找到元素"}

    def _clear(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """清空输入框"""
        element = self._find_element(params.get("locator"))
        if element:
            element.clear()
            return {"success": True, "message": "输入框已清空"}
        return {"success": False, "message": "未找到元素"}

    def _select(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """下拉选择"""
        element = self._find_element(params.get("locator"))
        if element:
            select = Select(element)
            value = params.get("value", "")
            select.select_by_visible_text(value)
            return {"success": True, "message": f"已选择: {value}"}
        return {"success": False, "message": "未找到元素"}

    def _checkbox(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """复选框操作"""
        element = self._find_element(params.get("locator"))
        if element:
            checked = params.get("checked", True)
            if element.is_selected() != checked:
                element.click()
            return {"success": True, "message": f"复选框已{'选中' if checked else '取消选中'}"}
        return {"success": False, "message": "未找到元素"}

    # ==================== 断言方法 ====================

    def _assert_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证页面文本"""
        expected_text = params.get("text", "")
        locator = params.get("locator", {})

        if locator and locator.get("value"):
            # 在元素中查找
            element = self._find_element(locator)
            if element:
                actual_text = element.text
            else:
                return {"success": False, "message": "未找到元素"}
        else:
            # 在整个页面中查找
            actual_text = self.driver.find_element(By.TAG_NAME, "body").text

        if expected_text in actual_text:
            return {"success": True, "message": f"文本验证通过: {expected_text}"}
        else:
            return {
                "success": False,
                "message": f"文本验证失败，期望包含: {expected_text}，实际: {actual_text}",
                "screenshot": self._capture_screenshot()
            }

    def _assert_title(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证页面标题"""
        expected = params.get("expected", "")
        actual = self.driver.title

        if expected == actual:
            return {"success": True, "message": f"标题验证通过: {expected}"}
        else:
            return {
                "success": False,
                "message": f"标题验证失败，期望: {expected}，实际: {actual}",
                "screenshot": self._capture_screenshot()
            }

    def _assert_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证页面URL"""
        expected = params.get("expected", "")
        actual = self.driver.current_url

        if expected == actual:
            return {"success": True, "message": f"URL验证通过: {expected}"}
        else:
            return {
                "success": False,
                "message": f"URL验证失败，期望: {expected}，实际: {actual}",
                "screenshot": self._capture_screenshot()
            }

    def _assert_element(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证元素存在"""
        element = self._find_element(params.get("locator"))
        if element:
            return {"success": True, "message": "元素存在"}
        return {
            "success": False,
            "message": "元素不存在",
            "screenshot": self._capture_screenshot()
        }

    def _assert_visible(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证元素可见"""
        element = self._find_element(params.get("locator"))
        if element and element.is_displayed():
            return {"success": True, "message": "元素可见"}
        return {
            "success": False,
            "message": "元素不可见",
            "screenshot": self._capture_screenshot()
        }

    # ==================== 等待方法 ====================

    def _wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """等待固定时间"""
        duration = params.get("duration", 1)
        time.sleep(duration)
        return {"success": True, "message": f"等待了 {duration} 秒"}

    def _wait_element(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """等待元素出现"""
        timeout = params.get("timeout", 10)
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self._by_locator(params.get("locator")))
            )
            return {"success": True, "message": "元素已出现"}
        except TimeoutException:
            return {
                "success": False,
                "message": f"等待元素超时（{timeout}秒）",
                "screenshot": self._capture_screenshot()
            }

    # ==================== 其他方法 ====================

    def _screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """截图"""
        screenshot_data = self._capture_screenshot()
        return {"success": True, "message": "截图成功", "screenshot": screenshot_data}

    def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """滚动页面"""
        scroll_type = params.get("scroll_type", "bottom")

        if scroll_type == "top":
            self.driver.execute_script("window.scrollTo(0, 0);")
        elif scroll_type == "bottom":
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif scroll_type == "custom":
            x = params.get("x", 0)
            y = params.get("y", 0)
            self.driver.execute_script(f"window.scrollTo({x}, {y});")

        return {"success": True, "message": f"已滚动到{scroll_type}"}

    def _upload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """文件上传"""
        locator = params.get("locator")
        file_path = params.get("file_path")

        if not locator or not file_path:
            return {"success": False, "message": "缺少locator或file_path参数"}

        try:
            element = self._find_element(locator)
            if element:
                element.send_keys(file_path)
                return {"success": True, "message": f"已上传文件: {file_path}"}
            return {"success": False, "message": "未找到文件输入元素"}
        except Exception as e:
            return {"success": False, "message": f"上传失败: {str(e)}"}

    def _download(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """文件下载"""
        url = params.get("url", "")
        save_path = params.get("save_path", "")
        wait_time = params.get("wait_time", 5)

        try:
            if url:
                # 导航到下载链接
                self.driver.get(url)

            # 等待下载完成
            time.sleep(wait_time)

            if save_path:
                return {"success": True, "message": f"文件已下载到: {save_path}"}
            return {"success": True, "message": "下载已触发"}
        except Exception as e:
            return {"success": False, "message": f"下载失败: {str(e)}"}


    # ==================== 辅助方法 ====================

    def _find_element(self, locator: Dict[str, Any]) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        查找元素

        Args:
            locator: 定位器 {type: str, value: str}

        Returns:
            找到的元素，未找到返回 None
        """
        if not locator or not locator.get("value"):
            return None

        try:
            by = self._by_locator(locator)
            return self.driver.find_element(by[0], by[1])
        except Exception as e:
            logger.debug(f"查找元素失败: {locator}, {e}")
            return None

    def _by_locator(self, locator: Dict[str, Any]) -> tuple:
        """
        将定位器转换为 Selenium 的 By 元组

        Args:
            locator: 定位器 {type: str, value: str}

        Returns:
            (By.XPATH, "//div") 格式的元组
        """
        locator_type = locator.get("type", "xpath")
        locator_value = locator.get("value", "")

        # 验证 value 不为空
        if not locator_value or not locator_value.strip():
            raise ValueError(f"定位器值不能为空 (type: {locator_type})")

        type_map = {
            "xpath": By.XPATH,
            "css": By.CSS_SELECTOR,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }

        by = type_map.get(locator_type, By.XPATH)
        return (by, locator_value)

    def _capture_screenshot(self) -> str:
        """
        截图并返回 Base64 编码

        Returns:
            Base64 编码的图片数据
        """
        try:
            screenshot = self.driver.get_screenshot_as_png()
            return base64.b64encode(screenshot).decode("utf-8")
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return ""


class ScriptExecutor:
    """
    脚本执行器

    负责执行完整的测试脚本（多个步骤）
    """

    def __init__(self):
        self.driver: Optional[webdriver.Remote] = None
        self.step_executor: Optional[StepExecutor] = None
        self.config = get_config_manager().get()

    def start(self, browser_type: str = "chrome") -> bool:
        """
        启动浏览器

        Args:
            browser_type: 浏览器类型 (chrome/firefox/edge)

        Returns:
            是否启动成功
        """
        try:
            if browser_type == "chrome":
                self.driver = self._create_chrome_driver()
            elif browser_type == "firefox":
                self.driver = self._create_firefox_driver()
            elif browser_type == "edge":
                self.driver = self._create_edge_driver()
            else:
                logger.error(f"不支持的浏览器类型: {browser_type}")
                return False

            self.step_executor = StepExecutor(self.driver)
            logger.info(f"浏览器启动成功: {browser_type}")
            return True

        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            return False

    def _create_chrome_driver(self) -> webdriver.Chrome:
        """创建 Chrome WebDriver"""
        options = webdriver.ChromeOptions()

        # 配置浏览器路径
        if self.config.chrome_path:
            options.binary_location = self.config.chrome_path

        # 配置驱动路径
        from selenium.webdriver.chrome.service import Service
        service = None
        if self.config.chrome_driver_path:
            service = Service(executable_path=self.config.chrome_driver_path)

        # 通用配置
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--ignore-certificate-errors")

        # 每次启动使用新的临时用户数据目录，清除缓存
        import tempfile
        import os
        user_data_dir = tempfile.mkdtemp(prefix='chrome_profile_')
        options.add_argument(f"--user-data-dir={user_data_dir}")

        if service:
            return webdriver.Chrome(service=service, options=options)
        else:
            # 使用 webdriver-manager 自动管理驱动
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)

    def _create_firefox_driver(self) -> webdriver.Firefox:
        """创建 Firefox WebDriver"""
        options = webdriver.FirefoxOptions()

        # 配置浏览器路径
        if self.config.firefox_path:
            options.binary_location = self.config.firefox_path

        # 配置驱动路径
        from selenium.webdriver.firefox.service import Service
        service = None
        if self.config.firefox_driver_path:
            service = Service(executable_path=self.config.firefox_driver_path)
        else:
            from webdriver_manager.firefox import GeckoDriverManager
            service = Service(GeckoDriverManager().install())

        return webdriver.Firefox(service=service, options=options)

    def _create_edge_driver(self) -> webdriver.Edge:
        """创建 Edge WebDriver"""
        options = webdriver.EdgeOptions()

        # 配置驱动路径
        from selenium.webdriver.edge.service import Service
        service = None
        if self.config.edge_driver_path:
            service = Service(executable_path=self.config.edge_driver_path)
        else:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            service = Service(EdgeChromiumDriverManager().install())

        return webdriver.Edge(service=service, options=options)

    def execute_script(
        self,
        script: Dict[str, Any],
        variables: Dict[str, Any] = None,
        on_step_complete: callable = None
    ) -> Dict[str, Any]:
        """
        执行脚本

        Args:
            script: 脚本数据 {steps: list, name: str}
            variables: 变量字典
            on_step_complete: 步骤完成回调 (step_index, step_result)

        Returns:
            执行结果 {success: bool, message: str, steps: list}
        """
        if not self.step_executor:
            return {"success": False, "message": "浏览器未启动"}

        steps = script.get("steps", [])
        script_name = script.get("name", "未命名脚本")

        logger.info(f"开始执行脚本: {script_name}，共 {len(steps)} 个步骤")

        results = []
        all_success = True

        for index, step in enumerate(steps):
            logger.info(f"执行步骤 {index + 1}/{len(steps)}: {step.get('name')}")

            step_result = self.step_executor.execute(step, variables)
            step_result["step_index"] = index
            results.append(step_result)

            # 回调
            if on_step_complete:
                on_step_complete(index, step_result)

            # 如果步骤失败且不继续
            if not step_result["success"]:
                all_success = False
                # TODO: 根据配置决定是否继续
                break

        if all_success:
            logger.info(f"脚本执行成功: {script_name}")
            return {
                "success": True,
                "message": "脚本执行成功",
                "steps": results
            }
        else:
            logger.error(f"脚本执行失败: {script_name}")
            return {
                "success": False,
                "message": "脚本执行失败",
                "steps": results
            }

    def stop(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.step_executor = None
            logger.info("浏览器已关闭")
