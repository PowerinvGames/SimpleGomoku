"""
游戏主窗口
整合所有UI组件，管理游戏界面和MCP服务器
"""
import arcade

from python.models.GameModels import GameResult, GameState, Position
from python.server.McpServer import McpServer
from python.ui.components.BoardView import BoardView
from python.ui.components.Button import Button
from python.ui.components.StatusPanel import StatusPanel
from python.util.Config import config
from python.util.Logger import logger


class GameWindow(arcade.Window):
    """游戏主窗口类"""
    
    def __init__(self, game_logic, mcp_server: McpServer = None):
        """初始化游戏窗口
        
        Args:
            game_logic: 游戏逻辑实例
            mcp_server: MCP服务器实例（可选）
        """
        # 从配置获取窗口设置
        width = config.get("window_width", 800)
        height = config.get("window_height", 600)
        title = config.get("window_title", "五子棋")
        self.bg_color = config.get("window_bg_color", (255, 255, 255))
        
        # 构建窗口标题
        title_text = title
        if mcp_server:
            mcp_url = mcp_server.get_server_info().get("url", "")
            title_text = title.format(http_host="", mcp_host=mcp_url)
        
        super().__init__(width, height, title_text)

        self.mcp_server = mcp_server
        
        # 使用外部传入的游戏逻辑
        self.game_logic = game_logic
        self.game_logic.set_event_handlers(
            on_state_change=self._on_game_state_change,
            on_move_made=self._on_move_made,
            on_game_over=self._on_game_over,
            on_force_redraw=self._force_redraw
        )
        
        # 字体路径
        self.font_path = config.get("font_path", "resources/HarmonyOS_SansSC_Regular.ttf")
        
        # 初始化UI组件
        self._init_ui()
        
        # 开始游戏
        self.game_logic.start_game()
        
        logger.info("游戏窗口初始化完成")
    
    def _init_ui(self):
        """初始化UI组件"""
        # 从配置获取尺寸
        board_size = config.get("board_size", 15)
        cell_size = config.get("cell_size", 35)
        board_margin = config.get("board_margin", 50)
        
        # 计算棋盘位置（居中）
        board_total_size = board_size * cell_size
        board_x = board_margin
        board_y = board_margin
        
        # 创建棋盘视图
        self.board_view = BoardView(
            x=board_x,
            y=board_y,
            board_size=board_size,
            cell_size=cell_size,
            on_cell_click=self._on_board_cell_click
        )

        button_width = config.get("button_width", 120)
        button_height = config.get("button_height", 40)
        button_spacing = config.get("button_spacing", 40)
        
        # 创建状态面板（在棋盘右侧）
        panel_width = button_width * 2 + button_spacing
        panel_height = self.height - board_margin * 3 - button_height * 2 - button_spacing
        panel_x = board_x + board_total_size + board_margin
        panel_y = self.height - panel_height - board_margin
        
        self.status_panel = StatusPanel(
            x=panel_x,
            y=panel_y,
            width=panel_width,
            height=panel_height
        )

        # 创建按钮
        
        # 新游戏按钮
        new_game_button_y = board_margin + button_height / 2 + button_height + button_spacing
        self.new_game_button = Button(
            x=panel_x + button_width / 2,
            y=new_game_button_y,
            width=button_width,
            height=button_height,
            text=config.get("text_new_game", "新游戏"),
            on_click=self._on_new_game_click
        )
        
        # 重新开始按钮
        self.restart_button = Button(
            x=panel_x + button_width / 2 + button_width + button_spacing,
            y=new_game_button_y,
            width=button_width,
            height=button_height,
            text=config.get("text_restart", "重新开始"),
            on_click=self._on_restart_click
        )
        
        # 悔棋按钮
        undo_button_y = board_margin + button_height / 2
        self.undo_button = Button(
            x=panel_x + button_width / 2,
            y=undo_button_y,
            width=button_width,
            height=button_height,
            text=config.get("text_retract_move", "悔棋"),
            on_click=self._on_undo_click
        )
        
        # 退出按钮
        self.quit_button = Button(
            x=panel_x + button_width / 2 + button_width + button_spacing,
            y=undo_button_y,
            width=button_width,
            height=button_height,
            text=config.get("text_quit", "退出游戏"),
            on_click=self._on_quit_click
        )
        
        # 存储所有按钮以便统一处理
        self.buttons = [
            self.new_game_button,
            self.restart_button,
            self.undo_button,
            self.quit_button
        ]
    
    def _update_status_panel(self):
        """更新状态面板"""
        game_state = self.game_logic.get_game_state()
        current_player = self.game_logic.get_current_player()
        move_count = len(self.game_logic.board.move_history)
        
        self.status_panel.update_status(
            game_state=game_state,
            current_player=current_player,
            move_count=move_count
        )
    
    def _update_board_view(self):
        """更新棋盘视图"""
        board_state = self.game_logic.get_board_state()
        self.board_view.update_board_state(board_state)
        
        # 如果有获胜连子，高亮显示
        game_result = self.game_logic.get_game_result()
        if game_result and game_result.winning_positions:
            self.board_view.set_highlighted_positions(game_result.winning_positions)
        else:
            self.board_view.clear_highlights()
    
    def _on_board_cell_click(self, row: int, col: int):
        """处理棋盘格子点击"""
        if self.game_logic.make_move(row, col):
            self._update_board_view()
            self._update_status_panel()
    
    def _on_new_game_click(self):
        """处理新游戏按钮点击"""
        logger.info("新游戏按钮点击")
        self.game_logic.start_game()
        self._update_board_view()
        self._update_status_panel()
    
    def _on_restart_click(self):
        """处理重新开始按钮点击"""
        logger.info("重新开始按钮点击")
        self.game_logic.restart_game()
        self._update_board_view()
        self._update_status_panel()
    
    def _on_undo_click(self):
        """处理悔棋按钮点击"""
        logger.info("悔棋按钮点击")
        if self.game_logic.undo_move():
            self._update_board_view()
            self._update_status_panel()
    
    def _on_quit_click(self):
        """处理退出按钮点击"""
        logger.info("退出按钮点击")
        self.close()
    
    def _on_game_state_change(self, game_state: GameState):
        """处理游戏状态变化"""
        logger.info(f"游戏状态变化: {game_state.value}")
        self._update_status_panel()
        # 如果游戏结束，也需要更新棋盘视图以显示高亮
        if game_state in [GameState.BLACK_WIN, GameState.WHITE_WIN, GameState.DRAW]:
            self._update_board_view()
            # 强制重绘窗口
            self._force_redraw()
    
    def _on_move_made(self, player, position: Position):
        """处理落子事件"""
        logger.info(f"落子: {player.name} at ({position.row}, {position.col})")
        # 更新UI以反映游戏状态变化
        self._update_board_view()
        self._update_status_panel()
        # 强制重绘窗口
        self._force_redraw()
    
    def _on_game_over(self, game_result: GameResult):
        """处理游戏结束事件"""
        logger.info(f"游戏结束: {game_result}")
        self._update_board_view()
        self._update_status_panel()
        # 强制重绘窗口
        self._force_redraw()
    
    def on_draw(self):
        """绘制窗口内容"""
        # 清除背景
        arcade.set_background_color(arcade.color.WHITE)

        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            self.width,
            self.height,
            self.bg_color
        )
        
        # 绘制所有UI组件
        self.board_view.draw()
        self.status_panel.draw()
        
        for button in self.buttons:
            button.draw()
    
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """处理鼠标移动事件"""
        self.board_view.on_mouse_motion(x, y)
        
        for button in self.buttons:
            button.on_mouse_motion(x, y)
    
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """处理鼠标按下事件"""
        self.board_view.on_mouse_press(x, y, button)
        
        for btn in self.buttons:
            btn.on_mouse_press(x, y, button)
    
    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """处理鼠标释放事件"""
        for btn in self.buttons:
            btn.on_mouse_release(x, y, button)
    
    def on_key_press(self, symbol: int, modifiers: int):
        """处理键盘按下事件"""
        # ESC键退出
        if symbol == arcade.key.ESCAPE:
            self.close()
        
        # R键重新开始
        elif symbol == arcade.key.R:
            self._on_restart_click()
        
        # N键新游戏
        elif symbol == arcade.key.N:
            self._on_new_game_click()
        
        # Z键悔棋
        elif symbol == arcade.key.Z and modifiers & arcade.key.MOD_CTRL:
            self._on_undo_click()
    
    def _force_redraw(self):
        """强制窗口重绘"""
        # 在arcade中，可以通过设置一个标志来触发重绘
        self._update_board_view()
        self._update_status_panel()
    
    def on_update(self, delta_time: float):
        """更新游戏状态"""
        # 这里可以添加动画或其他实时更新逻辑
        pass
    
    def on_close(self):
        """窗口关闭时调用"""
        logger.info("游戏窗口正在关闭...")
        
        # 停止MCP服务器
        if self.mcp_server and self.mcp_server.is_running():
            self.mcp_server.stop()
            logger.info("MCP服务器已停止")
        
        # 调用父类的关闭方法
        super().on_close()
        
        logger.info("游戏窗口已关闭")