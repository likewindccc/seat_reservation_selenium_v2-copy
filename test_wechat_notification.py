#!/usr/bin/env python3
"""
微信通知功能测试脚本

测试企业微信机器人通知是否正常工作
"""

import asyncio
from src.config.settings import settings
from src.utils.wechat_notification import WeChatWorkNotifier


async def test_wechat_notification():
    """测试微信通知功能"""
    print("=" * 60)
    print("🧪 微信通知功能测试")
    print("=" * 60)
    print()
    
    # 检查配置
    if not settings.WECHAT_WORK_ENABLED:
        print("❌ 微信通知未启用")
        print("💡 请在 src/config/settings.py 中设置 WECHAT_WORK_ENABLED = True")
        return
    
    if not settings.WECHAT_WORK_WEBHOOK_URL:
        print("❌ 微信Webhook URL未配置")
        print("💡 请在 src/config/settings.py 中设置 WECHAT_WORK_WEBHOOK_URL")
        return
    
    print("✅ 配置检查通过")
    print(f"   Webhook URL: {settings.WECHAT_WORK_WEBHOOK_URL[:50]}...")
    print()
    
    # 创建通知器
    notifier = WeChatWorkNotifier(
        webhook_url=settings.WECHAT_WORK_WEBHOOK_URL,
        timeout=settings.WECHAT_WORK_TIMEOUT
    )
    
    # 测试1: 发送测试消息
    print("📤 测试1: 发送基础测试消息...")
    result = await notifier.send_test_message()
    if result['success']:
        print("   ✅ 测试消息发送成功")
    else:
        print(f"   ❌ 测试消息发送失败: {result['message']}")
    print()
    
    # 测试2: 发送成功通知
    print("📤 测试2: 发送预约成功通知...")
    result = await notifier.send_success_notification(
        seat_number=158,
        date="2025年10月31日",
        account_name="测试账户",
        attempts=3,
        room_name="研学中心学生工位",
        mention_all=False
    )
    if result['success']:
        print("   ✅ 成功通知发送成功")
    else:
        print(f"   ❌ 成功通知发送失败: {result['message']}")
    print()
    
    # 测试3: 发送失败通知
    print("📤 测试3: 发送预约失败通知...")
    result = await notifier.send_failure_notification(
        date="2025年10月31日",
        account_name="测试账户",
        attempts=5,
        error_message="所有座位不可用",
        room_name="研学中心学生工位",
        attempted_seats=[158, 160, 162],
        mention_all=False
    )
    if result['success']:
        print("   ✅ 失败通知发送成功")
    else:
        print(f"   ❌ 失败通知发送失败: {result['message']}")
    print()
    
    # 测试4: 发送双账户报告
    print("📤 测试4: 发送双账户报告...")
    test_results = [
        {
            'account_name': '账户1',
            'success': True,
            'seat_number': 158,
            'message': '预约成功'
        },
        {
            'account_name': '账户2',
            'success': False,
            'seat_number': None,
            'message': '所有座位不可用'
        }
    ]
    result = await notifier.send_dual_account_report(
        successful=1,
        failed=1,
        execution_time=45.2,
        results=test_results,
        mention_all=False
    )
    if result['success']:
        print("   ✅ 双账户报告发送成功")
    else:
        print(f"   ❌ 双账户报告发送失败: {result['message']}")
    print()
    
    # 显示统计信息
    stats = notifier.get_stats()
    print("=" * 60)
    print("📊 发送统计:")
    print(f"   总发送数: {stats['total_sent']}")
    print(f"   成功数: {stats['success_sent']}")
    print(f"   失败数: {stats['failed_sent']}")
    print(f"   成功率: {stats['success_rate']*100:.1f}%")
    print("=" * 60)
    print()
    print("🎉 测试完成！")
    print("💡 请检查企业微信群是否收到了测试消息")


if __name__ == "__main__":
    asyncio.run(test_wechat_notification())

