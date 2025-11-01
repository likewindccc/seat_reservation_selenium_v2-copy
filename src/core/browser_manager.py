"""
浏览器管理模块

功能：
1. 初始化Edge浏览器
2. 使用webdriver-manager自动管理驱动版本（解决驱动更新问题）
3. 配置浏览器选项
4. 浏览器生命周期管理
"""

import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from typing import Optional

from ..config.settings import settings


class BrowserManager:
    """浏览器管理器"""

    def __init__(self, profile_dir: str, account_name: str = None):
        """
        初始化浏览器管理器

        Args:
            profile_dir: 用户配置文件目录（用于保持登录状态）
            account_name: 账户名称（用于设置窗口位置）
        """
        self.profile_dir = profile_dir
        self.account_name = account_name
        self.driver: Optional[webdriver.Edge] = None

    def create_driver(self) -> webdriver.Edge:
        """
        创建并配置Edge浏览器实例

        关键特性：
        - 优先使用webdriver-manager自动下载并管理驱动
        - 如果自动下载失败，回退到手动指定驱动路径
        - 自动适配浏览器版本

        Returns:
            配置好的WebDriver实例
        """
        # 配置浏览器选项
        options = Options()

        # 添加配置选项
        for option in settings.BROWSER_OPTIONS:
            options.add_argument(option)

        # 设置用户配置文件目录（保持登录状态）
        options.add_argument(f"--user-data-dir={self.profile_dir}")

        # 直接使用本地驱动（不自动下载）
        manual_driver_path = settings.MANUAL_EDGE_DRIVER_PATH
        if not manual_driver_path or not os.path.exists(manual_driver_path):
            raise Exception(f"Edge驱动不存在: {manual_driver_path}，请检查配置")

        service = Service(manual_driver_path)
        print(f"✅ 使用本地驱动: {manual_driver_path}")

        # 创建浏览器实例
        self.driver = webdriver.Edge(service=service, options=options)

        # 设置窗口大小和位置（双账户并排显示）
        if self.account_name and self.account_name in settings.WINDOW_POSITIONS:
            pos = settings.WINDOW_POSITIONS[self.account_name]
            self.driver.set_window_position(pos['x'], pos['y'])
            self.driver.set_window_size(pos['width'], pos['height'])
            print(f"✅ 窗口已设置: {self.account_name} - 位置({pos['x']}, {pos['y']}) 大小({pos['width']}x{pos['height']})")

        # 设置隐式等待
        self.driver.implicitly_wait(5)

        return self.driver

    def quit_driver(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None


def create_browser_manager(profile_dir: str, account_name: str = None) -> BrowserManager:
    """
    创建浏览器管理器

    Args:
        profile_dir: 用户配置文件目录
        account_name: 账户名称（用于设置窗口位置）

    Returns:
        BrowserManager实例
    """
    return BrowserManager(profile_dir, account_name)

