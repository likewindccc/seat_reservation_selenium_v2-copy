"""
日期处理工具模块

功能：
1. 获取北京时间的明天日期
2. 生成目标日期的XPath定位器
3. 处理日期格式转换
"""

import pytz
from datetime import datetime, timedelta


class DateHelper:
    """日期处理助手"""

    def __init__(self):
        """初始化日期助手，设置北京时区"""
        self.beijing_tz = pytz.timezone("Asia/Shanghai")

    def get_tomorrow_date(self) -> dict:
        """
        获取明天的日期信息（北京时间）

        Returns:
            包含年、月、日信息的字典
            {
                'year': 2025,
                'month': 11,
                'day': 1,
                'day_str': '1',
                'year_month_text': '2025年11月',
                'month_mark_text': '11'
            }
        """
        now_beijing = datetime.now(self.beijing_tz)
        tomorrow = now_beijing + timedelta(days=1)

        return {
            'year': tomorrow.year,
            'month': tomorrow.month,
            'day': tomorrow.day,
            'day_str': str(tomorrow.day),
            'year_month_text': f"{tomorrow.year}年{tomorrow.month}月",
            'month_mark_text': str(tomorrow.month)
        }

    def generate_date_xpath(self, date_info: dict) -> str:
        """
        生成目标日期的XPath定位器

        Args:
            date_info: 日期信息字典（来自get_tomorrow_date）

        Returns:
            完整的XPath字符串
        """
        day_str = date_info['day_str']
        year_month_text = date_info['year_month_text']
        month_mark_text = date_info['month_mark_text']

        # 具体日期单元格的XPath部分
        day_specific_xpath_part = (
            f"/div[@role='gridcell' and contains(@class, 'van-calendar__day') "
            f"and not(contains(@class, 'van-calendar__day--disabled')) "
            f"and normalize-space(text()[1]) = '{day_str}' "
            f"and ./div[contains(@class, 'van-calendar__bottom-info') "
            f"and contains(text(), '可约')]]"
        )

        # 完整的XPath
        target_day_xpath = (
            f"//div[@class='van-calendar__month']"
            f"["
            f"    (./div[@class='van-calendar__month-title' "
            f"and normalize-space(.)='{year_month_text}'])"
            f"    or "
            f"    ("
            f"        ./div[@class='van-calendar__days']/"
            f"div[@class='van-calendar__month-mark' "
            f"and normalize-space(.)='{month_mark_text}']"
            f"        and "
            f"        not(./div[@class='van-calendar__month-title'])"
            f"    )"
            f"]"
            f"/div[@class='van-calendar__days']"
            f"{day_specific_xpath_part}"
        )

        return target_day_xpath

    def format_date_for_api(self, date_info: dict) -> str:
        """
        格式化日期为API所需格式（YYYY-MM-DD）

        Args:
            date_info: 日期信息字典

        Returns:
            格式化的日期字符串，如 "2025-11-01"
        """
        return f"{date_info['year']:04d}-{date_info['month']:02d}-{date_info['day']:02d}"


def get_date_helper() -> DateHelper:
    """
    获取日期助手实例

    Returns:
        DateHelper实例
    """
    return DateHelper()

