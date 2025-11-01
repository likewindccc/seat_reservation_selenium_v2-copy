"""
配置管理模块

集中管理所有配置项：
1. 账户配置
2. URL配置
3. 路径配置
4. 浏览器配置
5. 超时配置
"""

import os


class Settings:
    """配置管理类"""

    # ==================== URL配置 ====================
    LOGIN_URL = (
        'https://m.ruc.edu.cn/uc/wap/login?redirect=https%3A%2F%2F'
        'm.ruc.edu.cn%2Fsite%2FapplicationSquare%2Findex%3Fsid%3D23'
    )

    # HTTP座位查询API（复用原HTTP版本）
    SEAT_QUERY_API = 'https://yxkj.ruc.edu.cn/kyq/static/frontApi/seat/getSeatStatus'
    AUTH_API = 'https://yxkj.ruc.edu.cn/kyq/static/frontApi/auth/generateToken'

    # ==================== 路径配置 ====================
    # 项目根目录
    PROJECT_ROOT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # 日志目录
    LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

    # 错误截图目录
    ERROR_DIR = os.path.join(PROJECT_ROOT, 'errors')

    # ==================== 浏览器配置 ====================
    # 浏览器类型
    BROWSER_TYPE = 'edge'

    # 手动指定Edge驱动路径（备选方案，当自动下载失败时使用）
    # 如果webdriver-manager自动下载失败，会使用此路径
    # 留空则仅使用自动下载方式
    MANUAL_EDGE_DRIVER_PATH = r"C:\edgedriver_win64\msedgedriver.exe"

    # 浏览器选项
    BROWSER_OPTIONS = [
        '--disable-gpu',                  # 禁用GPU加速
        '--no-sandbox',                   # 禁用沙箱模式
        '--disable-dev-shm-usage',        # 禁用/dev/shm使用
        '--disable-extensions',           # 禁用扩展
    ]
    
    # 窗口大小和位置配置（双账户并排显示）
    WINDOW_POSITIONS = {
        'Account1': {'x': 0, 'y': 0, 'width': 700, 'height': 1000},      # 左侧窗口
        'Account2': {'x': 700, 'y': 0, 'width': 700, 'height': 1000}     # 右侧窗口
    }

    # ==================== 超时配置 ====================
    # 全局超时（秒）
    GLOBAL_TIMEOUT = 300  # 5分钟

    # 元素等待超时（秒）
    ELEMENT_WAIT_TIMEOUT = 10

    # 验证码识别超时（秒）
    CAPTCHA_TIMEOUT = 120

    # 最大验证码尝试次数
    MAX_CAPTCHA_ATTEMPTS = 10
    
    # 滑块距离微调（像素）
    # 如果发现总是偏左（滑块没到位），设置为正数如 +5
    # 如果发现总是偏右（滑块过头），设置为负数如 -5
    SLIDER_DISTANCE_OFFSET = 0
    SLIDER_SAFE_MARGIN = 0
    SLIDER_MIN_VALID_DISTANCE = 10
    
    # ==================== 微信通知配置 📱 ====================
    # 是否启用微信通知（如不需要，设置为False）
    WECHAT_WORK_ENABLED = False
    
    # 企业微信机器人Webhook URL
    # 获取方式：企业微信群 -> 群设置 -> 群机器人 -> 添加机器人 -> 复制Webhook地址
    # 示例：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的机器人key
    WECHAT_WORK_WEBHOOK_URL = ""  # 请填写你的企业微信Webhook URL
    
    # 是否@所有人
    WECHAT_WORK_MENTION_ALL = False
    
    # 微信通知超时时间（秒）
    WECHAT_WORK_TIMEOUT = 10
    
    # 通知开关
    NOTIFY_ON_SUCCESS = True  # 预约成功时发送通知
    NOTIFY_ON_FAILURE = True  # 预约失败时发送通知
    NOTIFY_ON_EXCEPTION = True  # 发生异常时发送通知
    
    # ==================== 预约配置 ====================
    # 目标房间名称
    TARGET_ROOM = '研学中心学生工位'

    # ==================== 账户配置 ====================
    # 多账户配置列表
    # 每个账户独立运行，可以同时预约不同座位
    ACCOUNTS = [
        {
            'username': '',  # 请填写你的学工号
            'password': '',  # 请填写你的密码
            'account_name': 'Account1',  # 账户名称（用于日志区分）
            'seat_numbers': [158, 160, 162],  # 座位号列表（按优先级从高到低）
            'profile_dir': 'C:\\temp\\edge_profile_account1'  # Edge浏览器配置文件目录
        },
        # 如果需要第二个账户，请取消下面的注释并填写信息
        # {
        #     'username': '',  # 第二个账户的学工号
        #     'password': '',  # 第二个账户的密码
        #     'account_name': 'Account2',
        #     'seat_numbers': [159, 161, 163],
        #     'profile_dir': 'C:\\temp\\edge_profile_account2'
        # }
    ]

    # ==================== XPath定位器配置 ====================
    class XPath:
        """XPath定位器集合"""

        # 登录页面
        USERNAME_INPUT = "//input[@placeholder='学工号']"
        PASSWORD_INPUT = "//input[@placeholder='密码']"
        LOGIN_BUTTON = "//div[@class='btn' and normalize-space(text())='登 录']"

        # 应用入口
        APP_ENTRY_IMAGE = (
            "//img[@src='https://img.ruc.edu.cn/image/10/78da0b871d71402046f2d2055fcc2cb7.png']"
        )

        # 主界面
        APP_ICON = "//div[contains(@class, 'icon-wrap')] | //div[contains(@class, 'tabbar-word-wrap')]"
        IKNOW_BUTTON = "//span[contains(@class, 'pass') and contains(text(), '我知道了')]"
        
        # 滑块验证成功后的确定按钮
        SLIDER_CONFIRM_BUTTON = "//div[text()='确定']"

        # 预约选座
        SEAT_SELECT_TAB = (
            "//div[contains(@class, 'tabbar-word-wrap') and "
            "contains(normalize-space(text()), '预约选座')]"
        )

        # 房间列表
        ROOM_LIST = "//div[contains(@class, 'room-name')]"

        # 日期选择
        DATE_PICKER = "//div[@class='top-wrap']"
        CALENDAR_GRID = "//div[@class='van-calendar__days']"
        CONFIRM_DATE_BUTTON = "//button[contains(@class, 'van-calendar__confirm')]"

        # 座位选择
        SEAT_MAP = "//div[contains(@class, 'seat-item-wrap')] | //div[@class='word-wrap']"
        SEAT_ITEM = "//div[contains(@class, 'seat-item-wrap')]//div[contains(@class, 'word-wrap')]"

        # 确认按钮（选座后的确定按钮）
        CONFIRM_BUTTON = "//div[contains(@data-v, '') and normalize-space(text())='确定']"

        # 滑块验证码（tianai-captcha组件）
        SLIDER_CAPTCHA_POPUP = "//div[@id='tianai-captcha-parent']"
        SLIDER_BG_IMG = "//img[@id='tianai-captcha-slider-bg-img']"
        # 滑块模板图通过CSS的background-image设置在SLIDER_BUTTON上
        SLIDER_BUTTON = "//div[@id='tianai-captcha-slider-move-btn']"

        # 错误提示
        ERROR_TOAST = "//div[contains(@class, 'van-toast--text')]"
        SEAT_UNAVAILABLE = "//div[contains(@class, 'van-toast--text') and contains(text(), '该座位不可预约')]"

        # 成功提示
        SUCCESS_MESSAGE = "//*[contains(text(), '预约成功')] | //*[contains(text(), '提交成功')]"

        @staticmethod
        def get_room_xpath(room_name: str) -> str:
            """生成房间选择的XPath"""
            return f"//div[contains(@class, 'room-name') and contains(text(), '{room_name}')]"

        @staticmethod
        def get_seat_xpath(seat_number: int) -> str:
            """生成座位选择的XPath"""
            return (
                f"//div[contains(@class, 'seat-item-wrap')]"
                f"//div[contains(@class, 'word-wrap') and "
                f"normalize-space(text())='{seat_number}']"
            )


# 创建全局配置实例
settings = Settings()

