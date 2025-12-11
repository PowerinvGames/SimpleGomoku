"""
棋盘视图组件
负责棋盘的绘制和交互
"""
from typing import Callable, Optional

import arcade

from python.models.GameModels import Player, Position
from python.util.Config import config
from python.util.Logger import logger


class BoardView:
    """棋盘视图类"""
    
    def __init__(self, 
                 x: float, 
                 y: float, 
                 board_size: int,
                 cell_size: float,
                 on_cell_click: Optional[Callable[[int, int], None]] = None):
        """
        初始化棋盘视图
        
        Args:
            x: 棋盘左上角x坐标
            y: 棋盘左上角y坐标
            board_size: 棋盘大小（格子数）
            cell_size: 每个格子的大小
            on_cell_click: 格子点击回调函数
        """
        self.x = x
        self.y = y
        self.board_size = board_size
        self.cell_size = cell_size
        self.on_cell_click = on_cell_click
        
        # 计算棋盘总尺寸
        self.total_size = board_size * cell_size
        
        # 棋子状态
        self.board_state = [[Player.NONE for _ in range(board_size)] for _ in range(board_size)]
        
        # 高亮位置（用于显示最后一步或获胜连子）
        self.highlighted_positions: list[Position] = []
        
        # 鼠标悬停位置
        self.hover_row: Optional[int] = None
        self.hover_col: Optional[int] = None
        
        logger.info(f"棋盘视图初始化: 位置({x}, {y}), 大小{board_size}x{board_size}, 格子大小{cell_size}")
    
    def update_board_state(self, board_state: list[list[Player]]):
        """更新棋盘状态"""
        self.board_state = board_state
    
    def set_highlighted_positions(self, positions: list[Position]):
        """设置高亮位置"""
        self.highlighted_positions = positions
    
    def clear_highlights(self):
        """清除所有高亮"""
        self.highlighted_positions.clear()
    
    def draw(self):
        """绘制棋盘"""
        # 绘制棋盘背景
        board_color = config.get("board_color", (222, 184, 135))
        arcade.draw_lbwh_rectangle_filled(
            self.x,
            self.y,
            self.total_size,
            self.total_size,
            board_color
        )
        
        # 绘制网格线
        grid_color = config.get("grid_color", (139, 69, 19))
        line_width = 2
        
        # 绘制垂直线
        for i in range(self.board_size + 1):
            x = self.x + i * self.cell_size
            arcade.draw_line(
                x, self.y,
                x, self.y + self.total_size,
                grid_color, line_width
            )
        
        # 绘制水平线
        for i in range(self.board_size + 1):
            y = self.y + i * self.cell_size
            arcade.draw_line(
                self.x, y,
                self.x + self.total_size, y,
                grid_color, line_width
            )
        
        # 绘制棋子
        piece_radius = config.get("piece_radius", 15)
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                player = self.board_state[row][col]
                if player != Player.NONE:
                    # 计算棋子中心位置
                    center_x = self.x + col * self.cell_size + self.cell_size / 2
                    center_y = self.y + row * self.cell_size + self.cell_size / 2
                    
                    # 绘制棋子
                    color = player.get_color()
                    arcade.draw_circle_filled(center_x, center_y, piece_radius, color)
                    
                    # 绘制棋子边框
                    arcade.draw_circle_outline(center_x, center_y, piece_radius, (0, 0, 0), 1)
        
        # 绘制高亮位置
        if self.highlighted_positions:
            highlight_color = config.get("highlight_color", (255, 0, 0))
            for position in self.highlighted_positions:
                center_x = self.x + position.col * self.cell_size + self.cell_size / 2
                center_y = self.y + position.row * self.cell_size + self.cell_size / 2
                arcade.draw_circle_outline(center_x, center_y, piece_radius + 2, highlight_color, 3)
        
        # 绘制鼠标悬停提示
        if self.hover_row is not None and self.hover_col is not None:
            center_x = self.x + self.hover_col * self.cell_size + self.cell_size / 2
            center_y = self.y + self.hover_row * self.cell_size + self.cell_size / 2
            
            # 绘制半透明的悬停提示
            arcade.draw_circle_filled(center_x, center_y, piece_radius, (200, 200, 200, 100))
    
    def on_mouse_motion(self, x: float, y: float):
        """处理鼠标移动事件"""
        # 检查鼠标是否在棋盘范围内
        if (self.x <= x <= self.x + self.total_size and 
            self.y <= y <= self.y + self.total_size):
            
            # 计算对应的格子
            col = int((x - self.x) // self.cell_size)
            row = int((y - self.y) // self.cell_size)
            
            # 确保在有效范围内
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                self.hover_row = row
                self.hover_col = col
            else:
                self.hover_row = None
                self.hover_col = None
        else:
            self.hover_row = None
            self.hover_col = None
    
    def on_mouse_press(self, x: float, y: float, button: int):
        """处理鼠标点击事件"""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        
        # 检查鼠标是否在棋盘范围内
        if (self.x <= x <= self.x + self.total_size and 
            self.y <= y <= self.y + self.total_size):
            
            # 计算对应的格子
            col = int((x - self.x) // self.cell_size)
            row = int((y - self.y) // self.cell_size)
            
            # 确保在有效范围内
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                logger.info(f"棋盘点击: 位置({row}, {col})")
                
                # 调用点击回调
                if self.on_cell_click:
                    self.on_cell_click(row, col)
    
    def get_cell_center(self, row: int, col: int) -> tuple[float, float]:
        """
        获取指定格子的中心坐标
        
        Args:
            row: 行号
            col: 列号
            
        Returns:
            (x, y) 中心坐标
        """
        center_x = self.x + col * self.cell_size + self.cell_size / 2
        center_y = self.y + row * self.cell_size + self.cell_size / 2
        return center_x, center_y
    
    def contains_point(self, x: float, y: float) -> bool:
        """
        检查点是否在棋盘范围内
        
        Args:
            x: x坐标
            y: y坐标
            
        Returns:
            如果在范围内则返回True
        """
        return (self.x <= x <= self.x + self.total_size and 
                self.y <= y <= self.y + self.total_size)