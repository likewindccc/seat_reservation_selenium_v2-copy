"""
日志工具模块

功能：
1. 配置日志格式（仅记录ERROR级别）
2. 保存错误截图和HTML
3. 支持多账户日志区分
"""

import logging
import os
from datetime import datetime
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver


class Logger:
    """日志管理器，仅记录失败日志"""

    def __init__(self, name: str, log_dir: str = "logs",
                 error_dir: str = "errors"):
        """
        初始化日志管理器

        Args:
            name: 日志记录器名称（通常为账户名）
            log_dir: 日志文件存放目录
            error_dir: 错误截图和HTML存放目录
        """
        self.name = name
        self.log_dir = log_dir
        self.error_dir = error_dir

        # 创建目录
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(error_dir, exist_ok=True)

        # 配置日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.ERROR)

        # 仅在没有处理器时添加（避免重复）
        if not self.logger.handlers:
            # 文件处理器
            log_file = os.path.join(
                log_dir,
                f"error_{name}_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(
                log_file,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.ERROR)

            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)

            # 日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)

    def save_error_screenshot(self, driver: Optional[WebDriver],
                               error_type: str) -> bool:
        """
        保存错误截图和HTML

        Args:
            driver: WebDriver实例
            error_type: 错误类型（用于文件命名）

        Returns:
            是否保存成功
        """
        if not driver:
            self.error("WebDriver为空，无法保存错误截图")
            return False

        # 检查driver是否有效
        if not hasattr(driver, 'session_id') or not driver.session_id:
            self.error("WebDriver会话无效，无法保存错误截图")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存截图
        screenshot_path = os.path.join(
            self.error_dir,
            f"error_{error_type}_{self.name}_{timestamp}.png"
        )
        driver.save_screenshot(screenshot_path)

        # 保存HTML
        html_path = os.path.join(
            self.error_dir,
            f"error_{error_type}_{self.name}_{timestamp}.html"
        )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        self.error(f"错误信息已保存: {screenshot_path}")
        return True


def get_logger(account_name: str) -> Logger:
    """
    获取日志记录器

    Args:
        account_name: 账户名称

    Returns:
        Logger实例
    """
    return Logger(account_name)

