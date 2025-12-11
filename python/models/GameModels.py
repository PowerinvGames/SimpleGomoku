"""
游戏数据模型
定义游戏中的核心数据结构和枚举
"""
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List


class Player(Enum):
    """玩家枚举"""
    NONE = 0
    BLACK = 1
    WHITE = 2
    
    def opposite(self) -> 'Player':
        """获取对手玩家"""
        if self == Player.BLACK:
            return Player.WHITE
        elif self == Player.WHITE:
            return Player.BLACK
        return Player.NONE
    
    def get_color(self) -> Tuple[int, int, int]:
        """获取玩家对应的颜色"""
        from python.util.Config import config
        
        if self == Player.BLACK:
            return config.get("black_piece_color", (0, 0, 0))
        elif self == Player.WHITE:
            return config.get("white_piece_color", (255, 255, 255))
        return (128, 128, 128)  # 灰色


class GameState(Enum):
    """游戏状态枚举"""
    NOT_STARTED = "not_started"
    PLAYING = "playing"
    BLACK_WIN = "black_win"
    WHITE_WIN = "white_win"
    DRAW = "draw"
    PAUSED = "paused"


@dataclass
class Position:
    """棋盘位置"""
    row: int
    col: int
    
    def __post_init__(self):
        """验证位置有效性"""
        if not isinstance(self.row, int) or not isinstance(self.col, int):
            raise ValueError("行和列必须是整数")
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def to_tuple(self) -> Tuple[int, int]:
        """转换为元组"""
        return (self.row, self.col)
    
    @classmethod
    def from_tuple(cls, pos_tuple: Tuple[int, int]) -> 'Position':
        """从元组创建"""
        return cls(row=pos_tuple[0], col=pos_tuple[1])


@dataclass
class Move:
    """走棋记录"""
    player: Player
    position: Position
    move_number: int
    
    def __str__(self):
        return f"Move {self.move_number}: {self.player.name} at ({self.position.row}, {self.position.col})"


@dataclass
class GameResult:
    """游戏结果"""
    winner: Player
    winning_positions: List[Position]
    total_moves: int
    is_draw: bool = False
    
    def __str__(self):
        if self.is_draw:
            return "平局"
        return f"{self.winner.name} 获胜"


@dataclass
class GameSettings:
    """游戏设置"""
    board_size: int = 15
    win_count: int = 5
    allow_undo: bool = True
    max_undo_steps: int = 1000
    
    def validate(self):
        """验证设置有效性"""
        if self.board_size < 5:
            raise ValueError("棋盘大小不能小于5")
        if self.win_count < 3:
            raise ValueError("获胜连子数不能小于3")
        if self.win_count > self.board_size:
            raise ValueError("获胜连子数不能大于棋盘大小")
        if self.max_undo_steps < 0:
            raise ValueError("最大悔棋步数不能为负数")