"""
滑块验证码处理模块

功能：
1. 获取滑块验证码图片（从API）
2. 使用ddddocr识别滑动距离
3. 生成模拟人工的滑动轨迹
4. 执行滑块拖动操作
5. 验证结果判断

技术栈：
- ddddocr: 滑块距离识别
- ease-out算法: 生成人工轨迹
- ActionChains: 拖动操作
"""

import time
import base64
import ddddocr
from typing import List, Tuple, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import MoveTargetOutOfBoundsException

from ..config.settings import settings


class SliderCaptcha:
    """滑块验证码处理器"""

    def __init__(self, driver: WebDriver, logger):
        """
        初始化滑块验证码处理器

        Args:
            driver: WebDriver实例
            logger: 日志记录器
        """
        self.driver = driver
        self.logger = logger

        # 初始化ddddocr滑块识别器（关闭广告输出）
        self.slider_recognizer = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)

    def get_slider_images_from_api(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        从API响应中获取滑块图片

        实际使用中，滑块图片是通过JavaScript API获取的
        这里通过JavaScript执行来获取图片数据

        Returns:
            (背景图bytes, 滑块图bytes)，获取失败返回(None, None)
        """
        # 等待验证码API加载完成
        time.sleep(1)

        # 通过JavaScript获取图片数据
        # 实际项目中，这些图片数据可能存储在页面的某个变量中
        # 或者需要通过img/canvas元素获取
        bg_base64 = self.driver.execute_script("""
            // tianai-captcha 背景图
            var bgImg = document.getElementById('tianai-captcha-slider-bg-img');
            if (bgImg && bgImg.tagName === 'IMG') {
                return bgImg.src;
            }
            return null;
        """)

        slider_base64 = self.driver.execute_script("""
            // tianai-captcha 滑块图（优先从img元素获取，否则从CSS背景图获取）
            // 方法1：独立img元素
            var sliderImg = document.getElementById('tianai-captcha-slider-move-img');
            if (sliderImg && sliderImg.tagName === 'IMG' && sliderImg.src) {
                return sliderImg.src;
            }
            
            // 方法2：CSS背景图
            var sliderBtn = document.getElementById('tianai-captcha-slider-move-btn');
            if (sliderBtn) {
                var bgImg = window.getComputedStyle(sliderBtn).backgroundImage;
                if (bgImg && bgImg.startsWith('url')) {
                    // 提取 url("data:image/png;base64,...") 中的 data URI
                    var match = bgImg.match(/url\\(["']?(data:image\\/[^;]+;base64,[^"')]+)["']?\\)/);
                    if (match) {
                        return match[1];
                    }
                }
            }
            return null;
        """)

        if not bg_base64 or not slider_base64:
            self.logger.error("获取滑块图片失败")
            return None, None

        # 转换为bytes
        if 'base64,' in bg_base64:
            bg_base64 = bg_base64.split('base64,')[1]
        if 'base64,' in slider_base64:
            slider_base64 = slider_base64.split('base64,')[1]

        bg_bytes = base64.b64decode(bg_base64)
        slider_bytes = base64.b64decode(slider_base64)

        return bg_bytes, slider_bytes

    def recognize_distance(
        self,
        bg_bytes: bytes,
        slider_bytes: bytes
    ) -> int:
        """
        使用ddddocr识别滑块需要移动的距离

        Args:
            bg_bytes: 背景图bytes数据
            slider_bytes: 滑块图bytes数据

        Returns:
            滑动距离（像素），识别失败返回0
        """
        result = self.slider_recognizer.slide_match(
            slider_bytes,
            bg_bytes,
            simple_target=True
        )
        distance = result['target'][0]
        
        # 应用配置的距离偏移量（可在settings.py中调整）
        distance += settings.SLIDER_DISTANCE_OFFSET
        
        return distance

    def generate_track(self, distance: int) -> List[int]:
        """生成精细的人工滑动轨迹。"""
        target_distance = int(round(distance))
        if target_distance <= 0:
            return []

        import math

        raw_track: List[float] = []
        current = 0.0
        a1 = 50.0
        a2 = -50.0
        t = 0.1

        t_acc = math.sqrt(max(target_distance / a1, 0.0))
        mid_distance = 0.5 * a1 * t_acc * t_acc
        v = 0.0

        while current < target_distance:
            a = a1 if current < mid_distance else a2
            v_old = v
            v = max(0.0, v_old + a * t)
            move = v_old * t + 0.5 * a * t * t

            if current + move > target_distance:
                move = target_distance - current

            current += move

            if move >= 0.5:
                raw_track.append(move)

        if not raw_track:
            raw_track.append(float(target_distance))

        track = [max(1, int(round(step))) for step in raw_track]
        delta = target_distance - sum(track)
        track[-1] = max(1, track[-1] + delta)

        return track

    def calculate_scale_ratio(self) -> float:
        """
        计算背景图的缩放比例（显示宽度/原始宽度）
        
        ddddocr识别的坐标是基于原始图片的，但浏览器可能对图片进行了缩放。
        需要计算缩放比例来调整实际移动距离。
        
        Returns:
            float: 缩放比例（默认为1.0）
        """
        try:
            result = self.driver.execute_script("""
                var bgImg = document.getElementById('tianai-captcha-slider-bg-img');
                if (!bgImg) {
                    return {success: false, error: '找不到背景图元素'};
                }
                
                // 获取图片的原始宽度和显示宽度
                var originalWidth = bgImg.naturalWidth;   // 图片原始宽度
                var displayedWidth = bgImg.clientWidth;   // 浏览器显示宽度
                
                if (originalWidth === 0) {
                    return {success: false, error: '原始宽度为0'};
                }
                
                return {
                    success: true,
                    originalWidth: originalWidth,
                    displayedWidth: displayedWidth,
                    ratio: displayedWidth / originalWidth
                };
            """)
            
            if result and result.get('success'):
                original_width = result['originalWidth']
                displayed_width = result['displayedWidth']
                ratio = result['ratio']
                
                print(f"📏 图片缩放比例:")
                print(f"   - 原始宽度: {original_width}px")
                print(f"   - 显示宽度: {displayed_width}px")
                print(f"   - 缩放比例: {ratio:.4f} ({ratio*100:.2f}%)")
                
                return ratio
            else:
                error_msg = result.get('error', '未知错误') if result else '脚本返回空'
                print(f"⚠️  获取缩放比例失败: {error_msg}，使用默认比例1.0")
                return 1.0
                
        except Exception as e:
            self.logger.error(f"计算缩放比例异常: {e}")
            return 1.0
    
    def drag_slider(self, track: List[int]) -> bool:
        """
        执行滑块拖动操作

        Args:
            track: 滑动轨迹列表

        Returns:
            拖动是否成功
        """
        # 定位滑块按钮（tianai-captcha）
        slider_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, settings.XPath.SLIDER_BUTTON)
            )
        )

        # 创建动作链
        action = ActionChains(self.driver)

        try:
            action.click_and_hold(slider_btn).perform()

            for i, move in enumerate(track):
                action.move_by_offset(move, 0)
                if (i + 1) % 5 == 0 or i == len(track) - 1:
                    action.perform()

            action.release().perform()
            return True
        except MoveTargetOutOfBoundsException as exc:
            self.logger.error(f"拖动滑块时坐标超出范围: {exc}")
        except Exception as exc:
            self.logger.error(f"拖动滑块时发生异常: {exc}")
        finally:
            try:
                action.release()
            except Exception:
                pass

        return False

    def verify_result(self, timeout: float = 1.0) -> bool:
        """
        验证滑块验证是否成功

        Args:
            timeout: 等待验证结果的超时时间

        Returns:
            验证是否成功
        """
        time.sleep(timeout)

        # 检查验证码弹窗是否消失（tianai-captcha）
        slider_popups = self.driver.find_elements(
            By.XPATH,
            settings.XPath.SLIDER_CAPTCHA_POPUP
        )

        if not slider_popups:
            return True

        return False

    def handle_slider_captcha(self, max_attempts: int = 10) -> bool:
        """
        完整处理滑块验证码流程

        Args:
            max_attempts: 最大尝试次数

        Returns:
            验证是否成功
        """
        # 等待滑块验证框出现
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, settings.XPath.SLIDER_CAPTCHA_POPUP)
                )
            )
            time.sleep(0.2)
        except Exception as e:
            self.logger.error(f"滑块验证框未出现: {e}")
            return False

        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 第{attempt}次尝试滑块验证...")
            
            # 1. 获取滑块图片
            bg_bytes, slider_bytes = self.get_slider_images_from_api()
            if not bg_bytes or not slider_bytes:
                self.logger.error(f"第{attempt}次: 获取滑块图片失败")
                time.sleep(0.5)
                continue

            # 2. 识别需要移动的距离（ddddocr直接返回移动距离）
            distance = self.recognize_distance(bg_bytes, slider_bytes)
            
            print(f"✅ ddddocr识别移动距离: {distance}px（原始图片坐标系）")
            
            # 异常检测：识别距离过小可能是错误
            if distance < 20:
                print(f"⚠️  警告：识别距离异常小({distance}px)，可能是ddddocr识别错误")
            
            # 3. 计算图片缩放比例
            # 等待一下确保图片完全加载
            time.sleep(0.1)
            scale_ratio = self.calculate_scale_ratio()
            
            # 4. 根据缩放比例调整距离
            adjusted_distance = int(distance * scale_ratio)
            print(f"🎯 缩放调整后距离: {adjusted_distance}px (缩放比例 {scale_ratio:.4f})")
            
            # 5. 应用安全边距，避免过冲
            final_distance = adjusted_distance - settings.SLIDER_SAFE_MARGIN
            
            print(f"📏 最终移动距离: {final_distance}px (含安全边距 -{settings.SLIDER_SAFE_MARGIN}px)")
            
            # 6. 生成轨迹
            track = self.generate_track(final_distance)
            if not track:
                self.logger.error(f"第{attempt}次: 轨迹生成为空，滑动距离 {final_distance}px")
                time.sleep(0.5)
                continue
            total_move = sum(track)
            print(f"✅ 生成轨迹: {len(track)}个移动点，总移动{total_move}px")

            # 7. 拖动滑块
            if not self.drag_slider(track):
                self.logger.error(f"第{attempt}次: 拖动滑块失败")
                time.sleep(0.5)
                continue
            
            print(f"✅ 拖动完成，等待验证结果...")

            # 8. 验证结果
            if self.verify_result():
                print(f"🎉 滑块验证成功！")
                return True

            print(f"❌ 验证失败，准备重试...")
            self.logger.error(f"第{attempt}次: 滑块验证失败，重试...")
            time.sleep(0.5)

        self.logger.error(f"滑块验证失败，已达到最大尝试次数: {max_attempts}")
        return False


def create_slider_captcha(driver: WebDriver, logger) -> SliderCaptcha:
    """
    创建滑块验证码处理器

    Args:
        driver: WebDriver实例
        logger: 日志记录器

    Returns:
        SliderCaptcha实例
    """
    return SliderCaptcha(driver, logger)

