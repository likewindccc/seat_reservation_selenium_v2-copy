"""
HTTP座位查询模块

功能：
1. HTTP方式查询可用座位列表
2. 过滤可预约座位
3. 返回座位状态信息

注：这是一个简化版本，复用Selenium的登录token
实际使用中可以扩展为完整的HTTP查询系统
"""

import requests
from typing import List, Dict, Optional


class SeatQuery:
    """座位查询器"""

    def __init__(self, jwt_token: str, logger):
        """
        初始化座位查询器

        Args:
            jwt_token: JWT认证token（从Selenium登录获取）
            logger: 日志记录器
        """
        self.jwt_token = jwt_token
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def query_available_seats(
        self,
        room_id: str,
        date: str
    ) -> List[int]:
        """
        查询指定房间和日期的可用座位

        Args:
            room_id: 房间ID
            date: 日期（格式：YYYY-MM-DD）

        Returns:
            可用座位号列表
        """
        api_url = 'https://yxkj.ruc.edu.cn/kyq/static/frontApi/seat/getSeatStatus'

        # 构建查询参数
        params = {
            'roomId': room_id,
            'date': date
        }

        # 发送请求
        response = self.session.get(api_url, params=params)

        if response.status_code != 200:
            self.logger.error(f"查询座位失败，状态码: {response.status_code}")
            return []

        data = response.json()

        if not data.get('success'):
            self.logger.error(f"查询座位失败: {data.get('msg')}")
            return []

        # 解析座位数据
        seats = data.get('data', {}).get('seats', [])
        available_seats = [
            seat['seatNumber']
            for seat in seats
            if seat.get('status') == 'available'
        ]

        return available_seats

    def check_seat_available(
        self,
        room_id: str,
        date: str,
        seat_number: int
    ) -> bool:
        """
        检查指定座位是否可用

        Args:
            room_id: 房间ID
            date: 日期
            seat_number: 座位号

        Returns:
            是否可用
        """
        available_seats = self.query_available_seats(room_id, date)
        return seat_number in available_seats


def create_seat_query(jwt_token: str, logger) -> SeatQuery:
    """
    创建座位查询器

    Args:
        jwt_token: JWT认证token
        logger: 日志记录器

    Returns:
        SeatQuery实例
    """
    return SeatQuery(jwt_token, logger)

