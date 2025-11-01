"""
登录处理模块

功能：
1. 执行登录流程
2. 输入用户名密码
3. 点击登录按钮
4. 等待登录成功
5. 处理"我知道了"弹窗
"""

import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from ..config.settings import settings
from ..utils.element_helper import ElementHelper


class LoginHandler:
    """登录处理器"""

    def __init__(self, driver, element_helper: ElementHelper, logger):
        """
        初始化登录处理器

        Args:
            driver: WebDriver实例
            element_helper: 元素操作助手
            logger: 日志记录器
        """
        self.driver = driver
        self.helper = element_helper
        self.logger = logger

    def login(self, username: str, password: str) -> bool:
        """
        执行登录流程

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录是否成功
        """
        # 访问登录页面
        self.driver.get(settings.LOGIN_URL)

        # 等待并输入用户名
        username_input = self.helper.wait_for_element(
            (By.XPATH, settings.XPath.USERNAME_INPUT),
            timeout=15,
            condition="presence"
        )

        if not username_input:
            self.logger.error("未找到用户名输入框")
            return False

        username_input.send_keys(username)

        # 输入密码
        password_input = self.driver.find_element(
            By.XPATH,
            settings.XPath.PASSWORD_INPUT
        )
        password_input.send_keys(password)

        # 点击登录按钮并等待应用入口出现
        if not self.helper.click_and_wait(
            (By.XPATH, settings.XPath.LOGIN_BUTTON),
            (By.XPATH, settings.XPath.APP_ENTRY_IMAGE),
            description="登录按钮",
            wait_time=15
        ):
            self.logger.error("登录失败")
            return False

        # 进入应用
        if not self.helper.click_and_wait(
            (By.XPATH, settings.XPath.APP_ENTRY_IMAGE),
            (By.XPATH, settings.XPath.APP_ICON),
            description="应用入口",
            wait_time=15
        ):
            self.logger.error("进入应用失败")
            return False

        # 处理"我知道了"弹窗（可能存在）
        self._handle_iknow_popup()

        return True

    def _handle_iknow_popup(self):
        """处理"我知道了"弹窗（可能不存在）"""
        try:
            iknow_button = self.helper.wait_for_element(
                (By.XPATH, settings.XPath.IKNOW_BUTTON),
                timeout=5,
                condition="clickable"
            )

            if iknow_button:
                self.helper.safe_click(iknow_button, "我知道了按钮")
                time.sleep(0.5)
        except TimeoutException:
            # 弹窗不存在，正常跳过
            pass


def create_login_handler(driver, element_helper: ElementHelper, logger) -> LoginHandler:
    """
    创建登录处理器

    Args:
        driver: WebDriver实例
        element_helper: 元素操作助手
        logger: 日志记录器

    Returns:
        LoginHandler实例
    """
    return LoginHandler(driver, element_helper, logger)

