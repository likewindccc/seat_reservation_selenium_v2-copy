"""
预约流程编排模块

功能：
1. 进入预约选座界面
2. 选择目标房间
3. 选择目标日期（明天）
4. 选择座位
5. 触发验证码
6. 处理滑块验证码
7. 确认预约成功
"""

import time
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from ..config.settings import settings
from ..utils.element_helper import ElementHelper
from ..utils.date_helper import DateHelper
from .slider_captcha import SliderCaptcha


class ReservationHandler:
    """预约流程处理器"""

    def __init__(
        self,
        driver,
        element_helper: ElementHelper,
        date_helper: DateHelper,
        slider_captcha: SliderCaptcha,
        logger
    ):
        """
        初始化预约处理器

        Args:
            driver: WebDriver实例
            element_helper: 元素操作助手
            date_helper: 日期助手
            slider_captcha: 滑块验证码处理器
            logger: 日志记录器
        """
        self.driver = driver
        self.helper = element_helper
        self.date_helper = date_helper
        self.slider_captcha = slider_captcha
        self.logger = logger

    def enter_reservation_page(self) -> bool:
        """
        进入预约选座页面

        Returns:
            是否成功进入
        """
        # 点击预约选座标签
        if not self.helper.click_and_wait(
            (By.XPATH, settings.XPath.SEAT_SELECT_TAB),
            (By.XPATH, settings.XPath.ROOM_LIST),
            description="预约选座",
            wait_time=15
        ):
            self.logger.error("进入预约选座页面失败")
            return False

        return True

    def select_room(self, room_name: str = None) -> bool:
        """
        选择目标房间

        Args:
            room_name: 房间名称，None则使用默认配置

        Returns:
            是否选择成功
        """
        if room_name is None:
            room_name = settings.TARGET_ROOM

        room_xpath = settings.XPath.get_room_xpath(room_name)

        # 点击房间并等待日期选择器出现
        if not self.helper.click_and_wait(
            (By.XPATH, room_xpath),
            (By.XPATH, settings.XPath.DATE_PICKER),
            description=f"房间: {room_name}",
            wait_time=10
        ):
            self.logger.error(f"选择房间失败: {room_name}")
            return False

        # 等待日历加载
        calendar_element = self.helper.wait_for_element(
            (By.XPATH, settings.XPath.CALENDAR_GRID),
            timeout=10,
            condition="visible"
        )

        if not calendar_element:
            self.logger.error("日历加载失败")
            return False

        time.sleep(0.5)
        return True

    def select_date(self) -> bool:
        """
        选择明天的日期

        Returns:
            是否选择成功
        """
        # 获取明天的日期信息
        date_info = self.date_helper.get_tomorrow_date()

        # 生成日期XPath
        date_xpath = self.date_helper.generate_date_xpath(date_info)

        # 等待目标日期元素出现
        date_element = self.helper.wait_for_element(
            (By.XPATH, date_xpath),
            timeout=20,
            condition="presence"
        )

        if not date_element:
            self.logger.error(f"未找到目标日期: {date_info['day_str']}号")
            return False

        # 滚动到元素
        self.helper.scroll_to_element(date_element)
        time.sleep(0.5)

        # 等待元素可点击
        date_element = self.helper.wait_for_element(
            (By.XPATH, date_xpath),
            timeout=10,
            condition="clickable"
        )

        # 点击日期
        if not self.helper.safe_click(date_element, f"目标日期{date_info['day_str']}号"):
            self.logger.error("点击目标日期失败")
            return False

        time.sleep(0.5)

        # 确认日期
        if not self.helper.click_and_wait(
            (By.XPATH, settings.XPath.CONFIRM_DATE_BUTTON),
            (By.XPATH, settings.XPath.SEAT_MAP),
            description="日期确认按钮",
            wait_time=10
        ):
            self.logger.error("确认日期失败")
            return False

        # 等待座位图加载
        seat_item = self.helper.wait_for_element(
            (By.XPATH, settings.XPath.SEAT_ITEM),
            timeout=20,
            condition="visible"
        )

        if not seat_item:
            self.logger.error("座位图加载失败")
            return False

        time.sleep(0.5)
        return True

    def select_seat(self, seat_numbers: List[int]) -> bool:
        """
        选择座位（支持多个备选座位）

        Args:
            seat_numbers: 座位号列表（按优先级排序）

        Returns:
            是否选择成功
        """
        for seat_number in seat_numbers:
            seat_xpath = settings.XPath.get_seat_xpath(seat_number)

            # 尝试查找座位
            seat_element = self.helper.wait_for_element(
                (By.XPATH, seat_xpath),
                timeout=5,
                condition="clickable"
            )

            if not seat_element:
                self.logger.error(f"座位{seat_number}不可用，尝试下一个")
                continue

            # 点击座位
            if not self.helper.safe_click(seat_element, f"座位{seat_number}"):
                self.logger.error(f"点击座位{seat_number}失败")
                continue

            time.sleep(1)
            return True

        self.logger.error("所有备选座位均不可用")
        return False

    def confirm_reservation(self) -> bool:
        """
        点击确认按钮触发验证码

        Returns:
            验证码是否出现
        """
        # 点击确定按钮
        confirm_button = self.helper.wait_for_element(
            (By.XPATH, settings.XPath.CONFIRM_BUTTON),
            timeout=5,
            condition="clickable"
        )

        if not confirm_button:
            self.logger.error("未找到确定按钮")
            return False

        if not self.helper.safe_click(confirm_button, "确定按钮"):
            self.logger.error("点击确定按钮失败")
            return False

        # 等待验证码弹窗出现
        captcha_popup = self.helper.wait_for_element(
            (By.XPATH, settings.XPath.SLIDER_CAPTCHA_POPUP),
            timeout=15,
            condition="visible"
        )

        if not captcha_popup:
            self.logger.error("验证码弹窗未出现")
            return False

        return True

    def verify_success(self) -> bool:
        """
        验证预约是否成功

        Returns:
            是否成功
        """
        # 检查成功提示
        success_element = self.helper.wait_for_element(
            (By.XPATH, settings.XPath.SUCCESS_MESSAGE),
            timeout=5,
            condition="presence"
        )

        if success_element:
            return True

        # 如果验证码弹窗消失也认为可能成功
        captcha_popups = self.driver.find_elements(
            By.XPATH,
            settings.XPath.SLIDER_CAPTCHA_POPUP
        )

        return len(captcha_popups) == 0

    def reserve(self, seat_numbers: List[int]) -> bool:
        """
        执行完整预约流程

        Args:
            seat_numbers: 座位号列表（按优先级排序）

        Returns:
            预约是否成功
        """
        # 1. 进入预约页面
        if not self.enter_reservation_page():
            return False

        # 2. 选择房间
        if not self.select_room():
            return False

        # 3. 选择日期
        if not self.select_date():
            return False

        # 4. 选择座位
        if not self.select_seat(seat_numbers):
            return False

        # 5. 点击确认按钮
        if not self.confirm_reservation():
            return False

        # 6. 处理滑块验证码
        if not self.slider_captcha.handle_slider_captcha():
            self.logger.error("滑块验证失败")
            return False

        # 7. 验证成功
        if self.verify_success():
            return True

        self.logger.error("预约失败")
        return False


def create_reservation_handler(
    driver,
    element_helper: ElementHelper,
    date_helper: DateHelper,
    slider_captcha: SliderCaptcha,
    logger
) -> ReservationHandler:
    """
    创建预约处理器

    Args:
        driver: WebDriver实例
        element_helper: 元素操作助手
        date_helper: 日期助手
        slider_captcha: 滑块验证码处理器
        logger: 日志记录器

    Returns:
        ReservationHandler实例
    """
    return ReservationHandler(
        driver,
        element_helper,
        date_helper,
        slider_captcha,
        logger
    )

