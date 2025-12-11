"""
按钮组件
"""
import arcade
from typing import Optional, Callable
from python.Config import config
from python.Logger import logger


class Button:
    """按钮类"""
    
    def __init__(self, 
                 x: float, 
                 y: float, 
                 width: float, 
                 height: float,
                 text: str,
                 on_click: Optional[Callable[[], None]] = None,
                 font_size: Optional[int] = None):
        """
        初始化按钮
        
        Args:
            x: 按钮中心x坐标
            y: 按钮中心y坐标
            width: 按钮宽度
            height: 按钮高度
            text: 按钮文本
            on_click: 点击回调函数
            font_size: 字体大小，如果为None则使用配置中的默认值
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.on_click = on_click
        self.font_size = font_size or config.get("font_size", 20)
        
        # 按钮状态
        self.is_hovered = False
        self.is_pressed = False
        
        # 颜色配置
        self.normal_color = config.get("button_color", (70, 130, 180))
        self.hover_color = config.get("button_hover_color", (100, 149, 237))
        self.border_color = config.get("button_border_color", (255, 255, 255))
        self.text_color = config.get("button_text_color", (255, 255, 255))
        
        logger.debug(f"按钮创建: '{text}' 位置({x}, {y}), 大小{width}x{height}")
    
    def draw(self):
        """绘制按钮"""
        # 根据状态选择颜色
        if self.is_hovered:
            color = self.hover_color
        else:
            color = self.normal_color
        
        # 绘制按钮背景
        arcade.draw_lbwh_rectangle_filled(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height,
            color
        )
        
        # 绘制按钮边框
        arcade.draw_lbwh_rectangle_outline(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width, self.height,
            self.border_color,
            1
        )
        
        # 绘制按钮文本
        if not hasattr(self, '_button_text'):
            self._button_text = arcade.Text(
                self.text,
                self.x,
                self.y,
                self.text_color,
                self.font_size,
                anchor_x="center",
                anchor_y="center",
                align="left",
                width=int(self.width - 10)
            )
        else:
            self._button_text.text = self.text
            self._button_text.x = self.x
            self._button_text.y = self.y
        self._button_text.draw()
    
    def on_mouse_motion(self, x: float, y: float):
        """处理鼠标移动事件"""
        self.is_hovered = self.contains_point(x, y)
    
    def on_mouse_press(self, x: float, y: float, button: int):
        """处理鼠标按下事件"""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        
        if self.contains_point(x, y):
            self.is_pressed = True
    
    def on_mouse_release(self, x: float, y: float, button: int):
        """处理鼠标释放事件"""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        
        if self.is_pressed and self.contains_point(x, y):
            logger.info(f"按钮点击: '{self.text}'")
            if self.on_click:
                self.on_click()
        
        self.is_pressed = False
    
    def contains_point(self, x: float, y: float) -> bool:
        """
        检查点是否在按钮范围内
        
        Args:
            x: x坐标
            y: y坐标
            
        Returns:
            如果在范围内则返回True
        """
        half_width = self.width / 2
        half_height = self.height / 2
        
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)
    
    def set_text(self, text: str):
        """设置按钮文本"""
        self.text = text
    
    def set_on_click(self, on_click: Callable[[], None]):
        """设置点击回调函数"""
        self.on_click = on_click