"""
游戏逻辑类
管理游戏流程、状态转换、事件处理等高层逻辑
"""
from typing import Optional, Callable, List
from python.models.GameModels import Player, GameState, GameSettings, GameResult, Position
from python.core.Board import Board
from python.util.Logger import logger


class GameLogic:
    """游戏逻辑管理器"""
    
    def __init__(self, settings: Optional[GameSettings] = None):
        """
        初始化游戏逻辑
        
        Args:
            settings: 游戏设置
        """
        self.settings = settings or GameSettings()
        self.board = Board(self.settings)
        self.game_state = GameState.NOT_STARTED
        
        # 事件回调
        self.on_state_change: Optional[Callable[[GameState], None]] = None
        self.on_move_made: Optional[Callable[[Player, Position], None]] = None
        self.on_game_over: Optional[Callable[[GameResult], None]] = None
        
        logger.info("游戏逻辑初始化完成")
    
    def start_game(self):
        """开始新游戏"""
        self.board.reset()
        self.game_state = GameState.PLAYING
        
        logger.info("游戏开始")
        
        if self.on_state_change:
            self.on_state_change(self.game_state)
    
    def restart_game(self):
        """重新开始游戏"""
        self.board.reset()
        self.game_state = GameState.PLAYING
        
        logger.info("游戏重新开始")
        
        if self.on_state_change:
            self.on_state_change(self.game_state)
    
    def make_move(self, row: int, col: int) -> bool:
        """
        处理玩家落子
        
        Args:
            row: 行号
            col: 列号
            
        Returns:
            如果落子成功则返回True
        """
        if self.game_state != GameState.PLAYING:
            logger.warning(f"游戏状态为 {self.game_state.value}，不能落子")
            return False
        
        success = self.board.make_move(row, col)
        
        if success:
            # 通知移动事件
            if self.on_move_made:
                position = Position(row, col)
                self.on_move_made(self.board.current_player.opposite(), position)
            
            # 检查游戏是否结束
            if self.board.is_game_over:
                self._handle_game_over()
        
        return success
    
    def _handle_game_over(self):
        """处理游戏结束"""
        game_result = self.board.get_game_result()
        
        if game_result and game_result.winner != Player.NONE:
            if game_result.winner == Player.BLACK:
                self.game_state = GameState.BLACK_WIN
            else:
                self.game_state = GameState.WHITE_WIN
        elif game_result and game_result.is_draw:
            self.game_state = GameState.DRAW
        else:
            self.game_state = GameState.PLAYING
            return
        
        logger.info(f"游戏结束: {self.game_state.value}")
        
        # 通知状态变化
        if self.on_state_change:
            self.on_state_change(self.game_state)
        
        # 通知游戏结束
        if self.on_game_over and game_result:
            self.on_game_over(game_result)
    
    def undo_move(self) -> bool:
        """
        悔棋一步
        
        Returns:
            如果悔棋成功则返回True
        """
        if self.game_state != GameState.PLAYING:
            logger.warning(f"游戏状态为 {self.game_state.value}，不能悔棋")
            return False
        
        success = self.board.undo_move()
        
        if success:
            # 游戏状态恢复为进行中
            self.game_state = GameState.PLAYING
            
            logger.info("悔棋成功")
            
            # 通知状态变化
            if self.on_state_change:
                self.on_state_change(self.game_state)
        
        return success
    
    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.board.current_player
    
    def get_game_state(self) -> GameState:
        """获取游戏状态"""
        return self.game_state
    
    def get_board_state(self) -> List[List[Player]]:
        """获取棋盘状态"""
        return self.board.get_board_state()
    
    def get_available_moves(self) -> List[Position]:
        """获取可用落子位置"""
        return self.board.get_available_moves()
    
    def get_game_result(self) -> Optional[GameResult]:
        """获取游戏结果"""
        return self.board.get_game_result()
    
    def is_position_valid(self, row: int, col: int) -> bool:
        """检查位置是否有效"""
        return self.board.is_valid_move(row, col)
    
    def get_cell(self, row: int, col: int) -> Player:
        """获取指定位置的棋子"""
        return self.board.get_cell(row, col)
    
    def set_event_handlers(self,
                          on_state_change: Optional[Callable[[GameState], None]] = None,
                          on_move_made: Optional[Callable[[Player, Position], None]] = None,
                          on_game_over: Optional[Callable[[GameResult], None]] = None):
        """
        设置事件处理器
        
        Args:
            on_state_change: 游戏状态变化回调
            on_move_made: 落子回调
            on_game_over: 游戏结束回调
        """
        self.on_state_change = on_state_change
        self.on_move_made = on_move_made
        self.on_game_over = on_game_over
        
        logger.info("事件处理器已设置")
    
    def __str__(self) -> str:
        """游戏状态字符串表示"""
        return (f"游戏状态: {self.game_state.value}\n"
                f"当前玩家: {self.get_current_player().name}\n"
                f"棋盘状态:\n{self.board}")