"""
棋盘逻辑类
管理棋盘状态、落子、胜负判断等核心逻辑
"""
from typing import List, Optional, Tuple, Set
from python.models.GameModels import Player, Position, GameResult, GameSettings
from python.Logger import logger


class Board:
    """棋盘类"""
    
    def __init__(self, settings: Optional[GameSettings] = None):
        """
        初始化棋盘
        
        Args:
            settings: 游戏设置，如果为None则使用默认设置
        """
        self.settings = settings or GameSettings()
        self.settings.validate()
        
        # 初始化棋盘状态
        self.size = self.settings.board_size
        self.win_count = self.settings.win_count
        self._board = [[Player.NONE for _ in range(self.size)] for _ in range(self.size)]
        
        # 游戏历史记录
        self.move_history: List[Tuple[Player, Position]] = []
        self.current_player = Player.BLACK
        
        # 胜负状态
        self.winner = Player.NONE
        self.winning_positions: List[Position] = []
        self.is_game_over = False
        
        logger.info(f"初始化棋盘: {self.size}x{self.size}, 获胜连子数: {self.win_count}")
    
    def reset(self):
        """重置棋盘"""
        self._board = [[Player.NONE for _ in range(self.size)] for _ in range(self.size)]
        self.move_history.clear()
        self.current_player = Player.BLACK
        self.winner = Player.NONE
        self.winning_positions.clear()
        self.is_game_over = False
        
        logger.info("棋盘已重置")
    
    def get_cell(self, row: int, col: int) -> Player:
        """
        获取指定位置的棋子
        
        Args:
            row: 行号 (0-based)
            col: 列号 (0-based)
            
        Returns:
            该位置的玩家，如果没有棋子则返回Player.NONE
            
        Raises:
            IndexError: 如果位置超出棋盘范围
        """
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError(f"位置({row}, {col})超出棋盘范围(0-{self.size-1})")
        
        return self._board[row][col]
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """
        检查落子是否有效
        
        Args:
            row: 行号
            col: 列号
            
        Returns:
            如果位置有效且为空则返回True
        """
        try:
            return self.get_cell(row, col) == Player.NONE
        except IndexError:
            return False
    
    def make_move(self, row: int, col: int, player: Optional[Player] = None) -> bool:
        """
        在指定位置落子
        
        Args:
            row: 行号
            col: 列号
            player: 落子玩家，如果为None则使用当前玩家
            
        Returns:
            如果落子成功则返回True，否则返回False
        """
        if self.is_game_over:
            logger.warning("游戏已结束，不能落子")
            return False
        
        if not self.is_valid_move(row, col):
            logger.warning(f"无效的落子位置: ({row}, {col})")
            return False
        
        # 确定落子玩家
        move_player = player or self.current_player
        
        # 落子
        self._board[row][col] = move_player
        position = Position(row, col)
        self.move_history.append((move_player, position))
        
        logger.info(f"玩家 {move_player.name} 在位置 ({row}, {col}) 落子")
        
        # 检查胜负
        if self._check_win(row, col, move_player):
            self.winner = move_player
            self.is_game_over = True
            logger.info(f"玩家 {move_player.name} 获胜!")
            return True
        
        # 检查平局
        if self._check_draw():
            self.is_game_over = True
            logger.info("游戏平局!")
            return True
        
        # 切换玩家
        self.current_player = move_player.opposite()
        return True
    
    def undo_move(self) -> bool:
        """
        悔棋一步
        
        Returns:
            如果悔棋成功则返回True，否则返回False
        """
        if not self.settings.allow_undo:
            logger.warning("游戏设置不允许悔棋")
            return False
        
        if not self.move_history:
            logger.warning("没有可悔棋的步骤")
            return False
        
        if self.settings.max_undo_steps > 0 and len(self.move_history) > self.settings.max_undo_steps:
            logger.warning(f"超过最大悔棋步数限制: {self.settings.max_undo_steps}")
            return False
        
        # 移除最后一步
        player, position = self.move_history.pop()
        self._board[position.row][position.col] = Player.NONE
        
        # 重置游戏状态
        self.winner = Player.NONE
        self.winning_positions.clear()
        self.is_game_over = False
        
        # 恢复当前玩家
        self.current_player = player
        
        logger.info(f"悔棋: 玩家 {player.name} 在位置 ({position.row}, {position.col})")
        return True
    
    def _check_win(self, row: int, col: int, player: Player) -> bool:
        """
        检查指定位置是否形成获胜连子
        
        Args:
            row: 行号
            col: 列号
            player: 玩家
            
        Returns:
            如果获胜则返回True
        """
        # 检查的四个方向: 水平、垂直、左上到右下、右上到左下
        directions = [
            (0, 1),   # 水平
            (1, 0),   # 垂直
            (1, 1),   # 左上到右下
            (1, -1)   # 右上到左下
        ]
        
        for dr, dc in directions:
            count = 1  # 当前位置已经有一个棋子
            positions = [Position(row, col)]
            
            # 正向检查
            for i in range(1, self.win_count):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.size and 0 <= c < self.size and self._board[r][c] == player:
                    count += 1
                    positions.append(Position(r, c))
                else:
                    break
            
            # 反向检查
            for i in range(1, self.win_count):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.size and 0 <= c < self.size and self._board[r][c] == player:
                    count += 1
                    positions.append(Position(r, c))
                else:
                    break
            
            # 如果达到获胜条件
            if count >= self.win_count:
                self.winning_positions = positions[:self.win_count]  # 只保留获胜的连子
                return True
        
        return False
    
    def _check_draw(self) -> bool:
        """
        检查是否平局（棋盘已满）
        
        Returns:
            如果平局则返回True
        """
        for row in range(self.size):
            for col in range(self.size):
                if self._board[row][col] == Player.NONE:
                    return False
        return True
    
    def get_board_state(self) -> List[List[Player]]:
        """
        获取当前棋盘状态
        
        Returns:
            棋盘状态的深拷贝
        """
        return [row.copy() for row in self._board]
    
    def get_available_moves(self) -> List[Position]:
        """
        获取所有可用的落子位置
        
        Returns:
            可用位置列表
        """
        moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self._board[row][col] == Player.NONE:
                    moves.append(Position(row, col))
        return moves
    
    def get_game_result(self) -> Optional[GameResult]:
        """
        获取游戏结果
        
        Returns:
            如果游戏结束则返回GameResult，否则返回None
        """
        if not self.is_game_over:
            return None
        
        is_draw = self.winner == Player.NONE and self._check_draw()
        
        return GameResult(
            winner=self.winner,
            winning_positions=self.winning_positions.copy(),
            total_moves=len(self.move_history),
            is_draw=is_draw
        )
    
    def __str__(self) -> str:
        """棋盘字符串表示"""
        lines = []
        lines.append(f"棋盘大小: {self.size}x{self.size}")
        lines.append(f"当前玩家: {self.current_player.name}")
        lines.append(f"游戏状态: {'结束' if self.is_game_over else '进行中'}")
        if self.is_game_over:
            if self.winner != Player.NONE:
                lines.append(f"获胜者: {self.winner.name}")
            else:
                lines.append("平局")
        lines.append(f"总步数: {len(self.move_history)}")
        return "\n".join(lines)