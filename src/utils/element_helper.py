"""
元素操作助手模块

功能：
1. 统一的元素等待逻辑
2. 安全点击（带重试机制）
3. 滚动到元素
4. 移除遮罩层
"""

import time
from typing import Tuple, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class ElementHelper:
    """元素操作助手"""

    def __init__(self, driver: WebDriver, default_timeout: int = 10):
        """
        初始化元素助手

        Args:
            driver: WebDriver实例
            default_timeout: 默认等待超时时间（秒）
        """
        self.driver = driver
        self.default_timeout = default_timeout

    def wait_for_element(
        self,
        locator: Tuple,
        timeout: int = None,
        condition: str = "presence"
    ) -> Union[WebElement, None]:
        """
        等待元素出现

        Args:
            locator: 元素定位器，如 (By.XPATH, "//div[@id='test']")
            timeout: 等待超时时间（秒），None则使用默认值
            condition: 等待条件
                - "presence": 元素在DOM中存在
                - "visible": 元素可见
                - "clickable": 元素可点击

        Returns:
            找到的元素，超时则返回None
        """
        if timeout is None:
            timeout = self.default_timeout

        wait = WebDriverWait(self.driver, timeout)

        # 根据条件选择等待方法
        if condition == "presence":
            ec_condition = EC.presence_of_element_located(locator)
        elif condition == "visible":
            ec_condition = EC.visibility_of_element_located(locator)
        elif condition == "clickable":
            ec_condition = EC.element_to_be_clickable(locator)
        else:
            ec_condition = EC.presence_of_element_located(locator)

        element = wait.until(ec_condition)
        return element

    def remove_overlays(self):
        """移除页面上的遮罩层"""
        self.driver.execute_script("""
            var overlays = document.getElementsByClassName('overlay');
            for(var i=0; i<overlays.length; i++){
                overlays[i].style.visibility = 'hidden';
            }
        """)

    def scroll_to_element(self, element: WebElement):
        """
        滚动到元素中心位置

        Args:
            element: 目标元素
        """
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            element
        )
        time.sleep(0.3)

    def safe_click(
        self,
        element: Union[WebElement, Tuple],
        description: str = "元素",
        retries: int = 3
    ) -> bool:
        """
        安全点击元素（带重试机制）

        Args:
            element: WebElement实例或定位器元组
            description: 元素描述（用于日志）
            retries: 重试次数

        Returns:
            是否点击成功
        """
        # 如果传入的是定位器，先等待元素
        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition="clickable")
            if not element:
                return False

        for attempt in range(retries):
            # 移除遮罩层
            self.remove_overlays()

            # 滚动到元素
            self.scroll_to_element(element)

            # 尝试点击
            self.driver.execute_script("arguments[0].click();", element)
            return True

        return False

    def click_and_wait(
        self,
        click_locator: Tuple,
        expected_locator: Tuple,
        description: str = "操作",
        retries: int = 3,
        wait_time: int = 10
    ) -> bool:
        """
        点击元素并等待预期元素出现

        Args:
            click_locator: 要点击的元素定位器
            expected_locator: 预期出现的元素定位器
            description: 操作描述
            retries: 重试次数
            wait_time: 等待时间

        Returns:
            操作是否成功
        """
        for attempt in range(retries):
            # 等待元素可点击
            element = self.wait_for_element(
                click_locator,
                timeout=wait_time,
                condition="clickable"
            )

            if not element:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return False

            # 点击元素
            if not self.safe_click(element, description):
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return False

            # 等待预期元素出现
            expected_element = self.wait_for_element(
                expected_locator,
                timeout=wait_time,
                condition="visible"
            )

            if expected_element:
                return True

            if attempt < retries - 1:
                time.sleep(1)

        return False


def get_element_helper(driver: WebDriver) -> ElementHelper:
    """
    获取元素助手实例

    Args:
        driver: WebDriver实例

    Returns:
        ElementHelper实例
    """
    return ElementHelper(driver)

