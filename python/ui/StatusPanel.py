"""
状态面板组件
显示游戏状态信息
"""
import arcade
from python.models.GameModels import Player, GameState
from python.Config import config
from python.Logger import logger


class StatusPanel:
    """状态面板类"""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        """
        初始化状态面板
        
        Args:
            x: 面板左上角x坐标
            y: 面板左上角y坐标
            width: 面板宽度
            height: 面板高度
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # 状态信息
        self.game_state = GameState.NOT_STARTED
        self.current_player = Player.BLACK
        self.move_count = 0
        self.status_text = ""
        
        # 颜色配置
        self.bg_color = config.get("status_bg_color", (240, 240, 240))
        self.border_color = config.get("status_border_color", (200, 200, 200))
        self.text_color = config.get("status_text_color", (50, 50, 50))
        self.font_size = config.get("status_font_size", 24)
        
        logger.debug(f"状态面板初始化: 位置({x}, {y}), 大小{width}x{height}")
    
    def update_status(self, 
                     game_state: GameState, 
                     current_player: Player, 
                     move_count: int,
                     status_text: str = ""):
        """
        更新状态信息
        
        Args:
            game_state: 游戏状态
            current_player: 当前玩家
            move_count: 步数
            status_text: 状态文本
        """
        self.game_state = game_state
        self.current_player = current_player
        self.move_count = move_count
        self.status_text = status_text
    
    def draw(self):
        """绘制状态面板"""
        # 绘制背景
        arcade.draw_lbwh_rectangle_filled(
            self.x,
            self.y,
            self.width,
            self.height,
            self.bg_color
        )
        
        # 绘制边框
        arcade.draw_lbwh_rectangle_outline(
            self.x,
            self.y,
            self.width,
            self.height,
            self.border_color,
            1
        )
        
        # 准备状态文本
        lines = []
        
        # 游戏状态
        if self.game_state == GameState.PLAYING:
            if self.current_player == Player.BLACK:
                lines.append(config.get("text_black_turn", "黑方回合"))
            else:
                lines.append(config.get("text_white_turn", "白方回合"))
        elif self.game_state == GameState.BLACK_WIN:
            lines.append(config.get("text_black_win", "黑方获胜！"))
        elif self.game_state == GameState.WHITE_WIN:
            lines.append(config.get("text_white_win", "白方获胜！"))
        elif self.game_state == GameState.DRAW:
            lines.append(config.get("text_draw", "平局！"))
        elif self.game_state == GameState.NOT_STARTED:
            lines.append("游戏未开始")
        elif self.game_state == GameState.PAUSED:
            lines.append("游戏暂停")
        
        # 步数信息
        lines.append(f"步数: {self.move_count}")
        
        # 自定义状态文本
        if self.status_text:
            lines.append(self.status_text)
        
        # 绘制文本
        line_height = self.font_size + 16
        start_y = self.y + self.height - line_height
        
        # 初始化文本对象列表
        if not hasattr(self, '_status_texts'):
            self._status_texts = []
        
        # 确保有足够的文本对象
        while len(self._status_texts) < len(lines):
            self._status_texts.append(arcade.Text(
                "",
                self.x + 10,
                0,
                self.text_color,
                self.font_size,
                width=int(self.width - 20)
            ))
        
        # 更新并绘制文本
        for i, line in enumerate(lines):
            y_pos = start_y - i * line_height
            text_obj = self._status_texts[i]
            text_obj.text = line
            text_obj.x = self.x + 10
            text_obj.y = y_pos
            text_obj.draw()
        
        # 绘制当前玩家指示器
        if self.game_state == GameState.PLAYING:
            indicator_x = self.x + 10
            indicator_y = start_y - (len(lines) + 1) * line_height
            
            # 绘制玩家颜色指示器
            player_color = self.current_player.get_color()
            player_x = indicator_x + 70
            arcade.draw_circle_filled(player_x, indicator_y, 15, player_color)
            arcade.draw_circle_outline(player_x, indicator_y, 15, (0, 0, 0), 1)
            
            # 绘制标签
            if not hasattr(self, '_current_label_text'):
                self._current_label_text = arcade.Text(
                    "当前",
                    indicator_x,
                    indicator_y,
                    self.text_color,
                    self.font_size,
                    anchor_y="center"
                )
            else:
                self._current_label_text.x = indicator_x
                self._current_label_text.y = indicator_y
            self._current_label_text.draw()
    
    def contains_point(self, x: float, y: float) -> bool:
        """
        检查点是否在面板范围内
        
        Args:
            x: x坐标
            y: y坐标
            
        Returns:
            如果在范围内则返回True
        """
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)