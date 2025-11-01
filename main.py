"""
座位预约系统 Selenium V2 - 主入口

功能：
1. 双账户并行预约
2. 自动处理滑块验证码
3. 全局超时控制
4. 错误日志记录
5. 微信通知推送
"""

import threading
import os
import asyncio
from datetime import datetime

from src.config.settings import settings
from src.core.browser_manager import create_browser_manager
from src.core.login_handler import create_login_handler
from src.core.slider_captcha import create_slider_captcha
from src.core.reservation_handler import create_reservation_handler
from src.utils.logger import get_logger
from src.utils.element_helper import get_element_helper
from src.utils.date_helper import get_date_helper
from src.utils.wechat_notification import WeChatWorkNotifier


# 全局结果存储
reservation_results = []
results_lock = threading.Lock()


def send_wechat_sync(notifier, coro):
    """同步包装器：在新事件循环中运行异步通知"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result
    except Exception as e:
        print(f"微信通知发送失败: {e}")
        return {'success': False, 'message': str(e)}


def run_account(account_config: dict):
    """
    单个账户的预约流程

    Args:
        account_config: 账户配置字典
    """
    account_name = account_config['account_name']
    username = account_config['username']
    password = account_config['password']
    seat_numbers = account_config['seat_numbers']
    profile_dir = account_config['profile_dir']

    # 初始化日志
    logger = get_logger(account_name)
    
    # 初始化微信通知器
    notifier = None
    if settings.WECHAT_WORK_ENABLED and settings.WECHAT_WORK_WEBHOOK_URL:
        notifier = WeChatWorkNotifier(
            webhook_url=settings.WECHAT_WORK_WEBHOOK_URL,
            timeout=settings.WECHAT_WORK_TIMEOUT
        )

    # 初始化浏览器管理器（传入账户名用于设置窗口位置）
    browser_manager = create_browser_manager(profile_dir, account_name)

    # 创建浏览器实例
    driver = browser_manager.create_driver()

    # 初始化各个模块
    element_helper = get_element_helper(driver)
    date_helper = get_date_helper()
    slider_captcha = create_slider_captcha(driver, logger)
    login_handler = create_login_handler(driver, element_helper, logger)
    reservation_handler = create_reservation_handler(
        driver,
        element_helper,
        date_helper,
        slider_captcha,
        logger
    )
    
    # 记录结果
    tomorrow_info = date_helper.get_tomorrow_date()
    target_date = date_helper.format_date_for_api(tomorrow_info)
    
    result = {
        'account_name': account_name,
        'success': False,
        'seat_number': None,
        'message': '',
        'date': target_date
    }

    # 执行预约流程
    # 1. 登录
    if not login_handler.login(username, password):
        logger.error(f"{account_name}: 登录失败")
        logger.save_error_screenshot(driver, "login_failed")
        result['message'] = '登录失败'
        browser_manager.quit_driver()
        
        # 记录结果
        with results_lock:
            reservation_results.append(result)
        
        # 发送失败通知
        if notifier and settings.NOTIFY_ON_FAILURE:
            send_wechat_sync(
                notifier,
                notifier.send_failure_notification(
                    date=result['date'],
                    account_name=account_name,
                    error_message='登录失败',
                    room_name=settings.TARGET_ROOM,
                    attempted_seats=seat_numbers,
                    mention_all=settings.WECHAT_WORK_MENTION_ALL
                )
            )
        return

    # 2. 预约
    reservation_result = reservation_handler.reserve(seat_numbers)
    if reservation_result:
        result['success'] = True
        result['seat_number'] = reservation_result.get('seat_number', seat_numbers[0])
        result['message'] = '预约成功'
        print(f"🎉 {account_name}: 预约成功 - 座位{result['seat_number']}！")
        
        # 发送成功通知
        if notifier and settings.NOTIFY_ON_SUCCESS:
            send_wechat_sync(
                notifier,
                notifier.send_success_notification(
                    seat_number=result['seat_number'],
                    date=result['date'],
                    account_name=account_name,
                    attempts=reservation_result.get('attempts', 1),
                    room_name=settings.TARGET_ROOM,
                    mention_all=settings.WECHAT_WORK_MENTION_ALL
                )
            )
    else:
        result['message'] = '预约失败 - 所有座位不可用'
        logger.error(f"{account_name}: 预约失败")
        logger.save_error_screenshot(driver, "reservation_failed")
        
        # 发送失败通知
        if notifier and settings.NOTIFY_ON_FAILURE:
            send_wechat_sync(
                notifier,
                notifier.send_failure_notification(
                    date=result['date'],
                    account_name=account_name,
                    error_message='所有座位不可用',
                    room_name=settings.TARGET_ROOM,
                    attempted_seats=seat_numbers,
                    mention_all=settings.WECHAT_WORK_MENTION_ALL
                )
            )
    
    # 记录结果
    with results_lock:
        reservation_results.append(result)

    # 保持浏览器打开5秒
    import time
    time.sleep(5)

    # 关闭浏览器
    browser_manager.quit_driver()


def force_exit():
    """超时强制退出"""
    print("❌ 脚本运行超时，自动退出！")
    os._exit(1)


def main():
    """主函数"""
    start_time = datetime.now()
    
    print("=" * 60)
    print("🚀 座位预约系统 Selenium V2")
    print("=" * 60)
    print()
    print("⚠️  系统特性：")
    print("  1. 双账户并行预约")
    print("  2. 自动识别滑块验证码（ddddocr）")
    print("  3. 自动管理Edge驱动（webdriver-manager）")
    print("  4. 支持多个备选座位")
    print("  5. 仅记录错误日志")
    print("  6. 微信通知推送")
    print()
    print("-" * 60)

    # 显示账户配置
    print("📋 账户配置：")
    for i, account in enumerate(settings.ACCOUNTS, 1):
        print(f"  {i}. {account['account_name']}")
        print(f"     用户名: {account['username']}")
        print(f"     座位号: {account['seat_numbers']}")
    print()
    
    # 显示微信通知状态
    if settings.WECHAT_WORK_ENABLED and settings.WECHAT_WORK_WEBHOOK_URL:
        print("📱 微信通知: ✅ 已启用")
    else:
        print("📱 微信通知: ❌ 未启用")
    print()
    print("-" * 60)
    print()

    # 启动超时计时器
    timeout_timer = threading.Timer(settings.GLOBAL_TIMEOUT, force_exit)
    timeout_timer.daemon = True
    timeout_timer.start()

    # 启动线程
    threads = []
    for account in settings.ACCOUNTS:
        thread = threading.Thread(
            target=run_account,
            args=(account,),
            name=f"Thread-{account['account_name']}"
        )
        threads.append(thread)
        thread.start()
        print(f"✅ 线程 {thread.name} 已启动")

        # 线程启动间隔
        import time
        time.sleep(2)

    print()
    print("-" * 60)
    print("⏳ 等待预约流程完成...")
    print()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 取消超时计时器
    if timeout_timer and timeout_timer.is_alive():
        timeout_timer.cancel()

    # 计算总耗时
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    print()
    print("=" * 60)
    print("🎉 所有账户预约流程结束")
    print("=" * 60)
    
    # 统计结果
    successful_count = sum(1 for r in reservation_results if r['success'])
    failed_count = len(reservation_results) - successful_count
    
    print()
    print("📊 预约结果汇总：")
    print(f"   总账户数: {len(reservation_results)}")
    print(f"   成功: {successful_count}")
    print(f"   失败: {failed_count}")
    print(f"   总耗时: {execution_time:.1f}秒")
    print()
    
    for result in reservation_results:
        status = "✅ 成功" if result['success'] else "❌ 失败"
        seat_info = f"座位{result['seat_number']}" if result['seat_number'] else result['message']
        print(f"   {result['account_name']}: {status} - {seat_info}")
    
    print()
    print("=" * 60)
    
    # 发送双账户报告通知
    if (settings.WECHAT_WORK_ENABLED and settings.WECHAT_WORK_WEBHOOK_URL 
        and len(reservation_results) > 1):
        try:
            notifier = WeChatWorkNotifier(
                webhook_url=settings.WECHAT_WORK_WEBHOOK_URL,
                timeout=settings.WECHAT_WORK_TIMEOUT
            )
            
            send_wechat_sync(
                notifier,
                notifier.send_dual_account_report(
                    successful=successful_count,
                    failed=failed_count,
                    execution_time=execution_time,
                    results=reservation_results,
                    mention_all=settings.WECHAT_WORK_MENTION_ALL
                )
            )
            print("📱 双账户报告已发送到企业微信")
        except Exception as e:
            print(f"📱 发送双账户报告失败: {e}")


if __name__ == "__main__":
    main()

