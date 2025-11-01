#!/usr/bin/env python3
"""
企业微信机器人通知模块

基于企业微信机器人Webhook API实现消息推送
支持文本消息、Markdown格式、@提醒等功能

功能特性:
- 🤖 企业微信机器人消息推送
- 📝 支持文本和Markdown格式
- 🔔 支持@所有人或指定用户
- ⏰ 消息发送状态监控
- 🔄 自动重试机制
- 📊 发送统计功能

使用示例:
    notifier = WeChatWorkNotifier(webhook_url="your_webhook_url")
    await notifier.send_success_notification(seat_number=140, date="2025-09-18")
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio


class WeChatWorkNotifier:
    """企业微信机器人通知器"""
    
    def __init__(self, webhook_url: str, timeout: int = 10, max_retries: int = 3):
        """
        初始化企业微信通知器
        
        Args:
            webhook_url: 企业微信机器人Webhook URL
            timeout: 请求超时时间(秒)
            max_retries: 最大重试次数
        """
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 发送统计
        self.stats = {
            'total_sent': 0,
            'success_sent': 0,
            'failed_sent': 0,
            'last_sent_time': None
        }
    
    def is_configured(self) -> bool:
        """检查是否已正确配置"""
        return bool(self.webhook_url and self.webhook_url.startswith('https://qyapi.weixin.qq.com'))
    
    async def send_text_message(self, content: str, mention_list: List[str] = None, 
                               mention_mobile_list: List[str] = None) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            content: 消息内容
            mention_list: @用户列表 (userid)，@所有人用["@all"]
            mention_mobile_list: @用户手机号列表
            
        Returns:
            发送结果字典
        """
        if not self.is_configured():
            return {
                'success': False,
                'message': '企业微信机器人未配置或配置错误',
                'error_code': 'NOT_CONFIGURED'
            }
        
        # 构造消息体
        message_data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        # 添加@提醒
        if mention_list:
            message_data["text"]["mentioned_list"] = mention_list
        
        if mention_mobile_list:
            message_data["text"]["mentioned_mobile_list"] = mention_mobile_list
        
        return await self._send_message(message_data)
    
    async def send_markdown_message(self, content: str) -> Dict[str, Any]:
        """
        发送Markdown格式消息
        
        Args:
            content: Markdown格式的消息内容
            
        Returns:
            发送结果字典
        """
        if not self.is_configured():
            return {
                'success': False,
                'message': '企业微信机器人未配置或配置错误',
                'error_code': 'NOT_CONFIGURED'
            }
        
        message_data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        return await self._send_message(message_data)
    
    async def _send_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送消息到企业微信
        
        Args:
            message_data: 消息数据
            
        Returns:
            发送结果字典
        """
        self.stats['total_sent'] += 1
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.debug(f"发送企业微信消息 (尝试 {attempt}/{self.max_retries})")
                
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(self.webhook_url, json=message_data) as response:
                        
                        # 记录发送时间
                        self.stats['last_sent_time'] = datetime.now()
                        
                        if response.status == 200:
                            result = await response.json()
                            
                            if result.get('errcode') == 0:
                                self.stats['success_sent'] += 1
                                self.logger.info("企业微信消息发送成功")
                                return {
                                    'success': True,
                                    'message': '消息发送成功',
                                    'response': result,
                                    'attempt': attempt
                                }
                            else:
                                error_msg = result.get('errmsg', '未知错误')
                                self.logger.warning(f"企业微信API返回错误: {error_msg}")
                                
                                # 某些错误不需要重试
                                if result.get('errcode') in [93000, 93004]:
                                    self.stats['failed_sent'] += 1
                                    return {
                                        'success': False,
                                        'message': f'企业微信API错误: {error_msg}',
                                        'error_code': result.get('errcode'),
                                        'retry': False
                                    }
                        else:
                            self.logger.warning(f"HTTP请求失败: {response.status}")
                
            except asyncio.TimeoutError:
                self.logger.warning(f"企业微信消息发送超时 (尝试 {attempt}/{self.max_retries})")
            except Exception as e:
                self.logger.error(f"企业微信消息发送异常: {e} (尝试 {attempt}/{self.max_retries})")
            
            # 重试延迟
            if attempt < self.max_retries:
                await asyncio.sleep(1)
        
        # 所有重试失败
        self.stats['failed_sent'] += 1
        return {
            'success': False,
            'message': f'企业微信消息发送失败，已重试{self.max_retries}次',
            'error_code': 'SEND_FAILED'
        }
    
    async def send_success_notification(self, seat_number: int, date: str, 
                                      account_name: str = "", attempts: int = 1, 
                                      room_name: str = "立德研学中心", 
                                      mention_all: bool = False) -> Dict[str, Any]:
        """
        发送预约成功通知
        
        Args:
            seat_number: 座位号
            date: 预约日期
            account_name: 账户名称
            attempts: 尝试次数
            room_name: 房间名称
            mention_all: 是否@所有人
            
        Returns:
            发送结果
        """
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # 构造消息内容
        content = f"""🎉 【座位预约成功】🎉

📍 座位信息: {seat_number}号座位
📅 预约日期: {date}
🏢 房间: {room_name}
👤 账户: {account_name}
⏰ 预约时间: {current_time}
🎯 尝试次数: {attempts}次

💡 预约系统自动化成功！请及时查看！"""
        
        mention_list = ["@all"] if mention_all else None
        return await self.send_text_message(content, mention_list=mention_list)
    
    async def send_failure_notification(self, date: str, account_name: str = "", 
                                      attempts: int = 1, error_message: str = "",
                                      room_name: str = "立德研学中心",
                                      attempted_seats: List[int] = None,
                                      mention_all: bool = False) -> Dict[str, Any]:
        """
        发送预约失败通知
        
        Args:
            date: 目标日期
            account_name: 账户名称
            attempts: 尝试次数
            error_message: 错误信息
            room_name: 房间名称
            attempted_seats: 尝试的座位列表
            mention_all: 是否@所有人
            
        Returns:
            发送结果
        """
        current_time = datetime.now().strftime("%H:%M:%S")
        seats_info = f"📋 尝试座位: {attempted_seats}" if attempted_seats else ""
        
        content = f"""❌ 【座位预约失败】❌

📅 目标日期: {date}
🏢 房间: {room_name}
👤 账户: {account_name}
⏰ 执行时间: {current_time}
🎯 尝试次数: {attempts}次
{seats_info}
📋 失败原因: {error_message}

💡 建议检查账户状态和座位可用性！"""
        
        mention_list = ["@all"] if mention_all else None
        return await self.send_text_message(content, mention_list=mention_list)
    
    async def send_dual_account_report(self, successful: int, failed: int, 
                                     execution_time: float, results: List[Dict],
                                     mention_all: bool = False) -> Dict[str, Any]:
        """
        发送双账户执行报告
        
        Args:
            successful: 成功账户数
            failed: 失败账户数
            execution_time: 执行时间
            results: 详细结果列表
            mention_all: 是否@所有人
            
        Returns:
            发送结果
        """
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # 构造结果详情
        result_details = []
        for i, result in enumerate(results):
            account_name = result.get('account_name', f'账户{i+1}')
            if result.get('success'):
                seat_number = result.get('seat_number', 'N/A')
                result_details.append(f"✅ {account_name}: 预约成功 - 座位{seat_number}")
            else:
                message = result.get('message', '未知错误')
                result_details.append(f"❌ {account_name}: 预约失败 - {message}")
        
        content = f"""📊 【双账户预约报告】📊

⏰ 执行时间: {current_time}
⏱️ 总耗时: {execution_time:.1f}秒
✅ 成功: {successful} 个账户
❌ 失败: {failed} 个账户

📋 详细结果:
{chr(10).join(result_details)}

💡 双账户并行预约{"成功" if successful > 0 else "失败"}！请及时查看！"""
        
        mention_list = ["@all"] if mention_all else None
        return await self.send_text_message(content, mention_list=mention_list)
    
    async def send_test_message(self) -> Dict[str, Any]:
        """
        发送测试消息
        
        Returns:
            发送结果
        """
        test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"""🧪 【通知测试】🧪

⏰ 测试时间: {test_time}
🤖 通知服务: 企业微信机器人
✅ 状态: 配置正常，连接成功！

💡 座位预约系统通知功能已就绪！"""
        
        return await self.send_text_message(content)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取发送统计信息"""
        stats = self.stats.copy()
        if stats['total_sent'] > 0:
            stats['success_rate'] = stats['success_sent'] / stats['total_sent']
        else:
            stats['success_rate'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_sent': 0,
            'success_sent': 0,
            'failed_sent': 0,
            'last_sent_time': None
        }


# 便捷函数
async def send_wechat_notification(webhook_url: str, message: str, 
                                 mention_all: bool = False) -> Dict[str, Any]:
    """
    便捷函数：发送企业微信通知
    
    Args:
        webhook_url: 企业微信机器人Webhook URL
        message: 消息内容
        mention_all: 是否@所有人
        
    Returns:
        发送结果
    """
    notifier = WeChatWorkNotifier(webhook_url)
    mention_list = ["@all"] if mention_all else None
    return await notifier.send_text_message(message, mention_list=mention_list)


async def test_wechat_configuration(webhook_url: str) -> Dict[str, Any]:
    """
    测试企业微信配置
    
    Args:
        webhook_url: 企业微信机器人Webhook URL
        
    Returns:
        测试结果
    """
    notifier = WeChatWorkNotifier(webhook_url)
    return await notifier.send_test_message()


if __name__ == "__main__":
    import asyncio
    
    async def test_notification():
        print("🧪 企业微信通知模块测试")
        
        webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
        
        if webhook_url == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY":
            print("❌ 请先配置正确的Webhook URL")
            return
        
        notifier = WeChatWorkNotifier(webhook_url)
        
        print(f"配置状态: {'✅ 已配置' if notifier.is_configured() else '❌ 未配置'}")
        
        if notifier.is_configured():
            result = await notifier.send_test_message()
            print(f"测试结果: {result}")
            print(f"发送统计: {notifier.get_stats()}")
    
    asyncio.run(test_notification())

