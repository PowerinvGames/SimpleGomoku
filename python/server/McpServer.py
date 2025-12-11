"""
MCP服务器管理器
管理MCP服务器的生命周期和与游戏逻辑的交互
"""
import threading
import time
from typing import Any, Dict

from fastmcp import FastMCP

from python.models.GameModels import GameState, Player
from python.util.Config import config
from python.util.Logger import logger
from python.util.PortFinder import PortFinder


class McpServer:
    """MCP服务器管理器"""
    
    def __init__(self, game_logic=None):
        """
        初始化MCP服务器
        
        Args:
            game_logic: 游戏逻辑实例（可选，可以稍后设置）
        """
        self.game_logic = game_logic
        self.mcp = None
        self.server_thread = None
        self.server_running = False
        self.server_port = self._get_available_port()  # 自动获取可用端口
        
        # 如果提供了game_logic，注册工具
        if game_logic:
            self._register_tools()
            logger.info(f"MCP服务器管理器初始化完成（已设置游戏逻辑），端口: {self.server_port}")
        else:
            logger.info(f"MCP服务器管理器初始化完成（游戏逻辑未设置），端口: {self.server_port}")
    
    def _get_available_port(self) -> int:
        """获取可用端口"""
        # 从配置获取设置
        min_port = config.get("mcp_server_min_port", 60000)
        max_port = config.get("mcp_server_max_port", 65535)

        # 自动查找可用端口
        logger.info(f"自动查找可用端口，范围: {min_port}-{max_port}")
        available_port = PortFinder.find_available_port(min_port, max_port)

        if available_port is not None:
            logger.info(f"找到可用端口: {available_port}")
            return available_port
        else:
            logger.warning(f"在范围 {min_port}-{max_port} 中未找到可用端口")
            return -1
    
    def _register_tools(self):
        """注册MCP工具"""
        # 创建FastMCP实例
        self.mcp = FastMCP("GomokuGame", version="1.0.0")
        
        # 注册工具：获取游戏状态
        @self.mcp.tool()
        def get_game_state() -> Dict[str, Any]:
            """获取当前游戏状态"""
            try:
                game_state = self.game_logic.get_game_state()
                current_player = self.game_logic.get_current_player()
                board_state = self.game_logic.get_board_state()
                available_moves = self.game_logic.get_available_moves()
                
                # 转换棋盘状态为可序列化的格式
                board_serializable = []
                for row in board_state:
                    board_serializable.append([player.name for player in row])
                
                # 转换可用位置
                moves_serializable = [(pos.row, pos.col) for pos in available_moves]
                
                return {
                    "game_state": game_state.value,
                    "current_player": current_player.name,
                    "board_size": len(board_state),
                    "board": board_serializable,
                    "available_moves": moves_serializable,
                    "move_count": len(self.game_logic.board.move_history)
                }
            except Exception as e:
                logger.error(f"获取游戏状态失败: {e}")
                return {"error": str(e)}
        
        # 注册工具：落子
        @self.mcp.tool()
        def make_move(row: int, col: int) -> Dict[str, Any]:
            """在指定位置落子"""
            try:
                # 检查位置是否有效
                if not self.game_logic.is_position_valid(row, col):
                    return {
                        "success": False,
                        "error": f"无效的位置: ({row}, {col})",
                        "available_moves": [(pos.row, pos.col) for pos in self.game_logic.get_available_moves()]
                    }
                
                # 执行落子
                success = self.game_logic.make_move(row, col)
                
                if success:
                    # 获取更新后的状态
                    game_state = self.game_logic.get_game_state()
                    current_player = self.game_logic.get_current_player()
                    
                    # 检查游戏是否结束
                    game_result = self.game_logic.get_game_result()
                    is_game_over = game_state in [GameState.BLACK_WIN, GameState.WHITE_WIN, GameState.DRAW]
                    
                    result = {
                        "success": True,
                        "position": (row, col),
                        "player": Player.BLACK.name if self.game_logic.get_current_player() == Player.WHITE else Player.WHITE.name,
                        "game_state": game_state.value,
                        "current_player": current_player.name,
                        "is_game_over": is_game_over
                    }
                    
                    if is_game_over and game_result:
                        result["game_result"] = {
                            "winner": game_result.winner.name,
                            "is_draw": game_result.is_draw,
                            "total_moves": game_result.total_moves
                        }
                    
                    return result
                else:
                    return {
                        "success": False,
                        "error": "落子失败",
                        "game_state": self.game_logic.get_game_state().value
                    }
                    
            except Exception as e:
                logger.error(f"落子失败: {e}")
                return {"success": False, "error": str(e)}
        
        # 注册工具：获取可用位置
        @self.mcp.tool()
        def get_available_moves() -> Dict[str, Any]:
            """获取所有可用的落子位置"""
            try:
                available_moves = self.game_logic.get_available_moves()
                moves = [(pos.row, pos.col) for pos in available_moves]
                
                return {
                    "available_moves": moves,
                    "count": len(moves)
                }
            except Exception as e:
                logger.error(f"获取可用位置失败: {e}")
                return {"error": str(e)}
        
        # 注册工具：开始新游戏
        @self.mcp.tool()
        def start_new_game() -> Dict[str, Any]:
            """开始新游戏"""
            try:
                self.game_logic.start_game()
                
                return {
                    "success": True,
                    "message": "新游戏已开始",
                    "game_state": self.game_logic.get_game_state().value,
                    "current_player": self.game_logic.get_current_player().name
                }
            except Exception as e:
                logger.error(f"开始新游戏失败: {e}")
                return {"success": False, "error": str(e)}
        
        # 注册工具：重新开始游戏
        @self.mcp.tool()
        def restart_game() -> Dict[str, Any]:
            """重新开始游戏"""
            try:
                self.game_logic.restart_game()
                
                return {
                    "success": True,
                    "message": "游戏已重新开始",
                    "game_state": self.game_logic.get_game_state().value,
                    "current_player": self.game_logic.get_current_player().name
                }
            except Exception as e:
                logger.error(f"重新开始游戏失败: {e}")
                return {"success": False, "error": str(e)}
        
        # 注册工具：悔棋
        @self.mcp.tool()
        def undo_move() -> Dict[str, Any]:
            """悔棋一步"""
            try:
                success = self.game_logic.undo_move()
                
                if success:
                    return {
                        "success": True,
                        "message": "悔棋成功",
                        "game_state": self.game_logic.get_game_state().value,
                        "current_player": self.game_logic.get_current_player().name
                    }
                else:
                    return {
                        "success": False,
                        "error": "悔棋失败",
                        "game_state": self.game_logic.get_game_state().value
                    }
            except Exception as e:
                logger.error(f"悔棋失败: {e}")
                return {"success": False, "error": str(e)}
        
        # 注册工具：获取游戏信息
        @self.mcp.tool()
        def get_game_info() -> Dict[str, Any]:
            """获取游戏详细信息"""
            try:
                game_state = self.game_logic.get_game_state()
                current_player = self.game_logic.get_current_player()
                board_state = self.game_logic.get_board_state()
                move_history = self.game_logic.board.move_history
                
                # 转换历史记录
                history = []
                for i, (player, position) in enumerate(move_history):
                    history.append({
                        "move_number": i + 1,
                        "player": player.name,
                        "position": (position.row, position.col)
                    })
                
                return {
                    "game_name": "五子棋",
                    "version": "1.0.0",
                    "game_state": game_state.value,
                    "current_player": current_player.name,
                    "board_size": len(board_state),
                    "total_moves": len(move_history),
                    "move_history": history,
                    "available_moves_count": len(self.game_logic.get_available_moves())
                }
            except Exception as e:
                logger.error(f"获取游戏信息失败: {e}")
                return {"error": str(e)}
        
        logger.info("MCP工具注册完成")
    
    def _run_server(self):
        """运行MCP服务器（在独立线程中）"""
        try:
            logger.info(f"启动MCP服务器，端口: {self.server_port}")
            
            # 运行MCP服务器
            self.mcp.run(transport="sse", port=self.server_port, host=config.get("mcp_server_host", "0.0.0.0"))
            
        except Exception as e:
            logger.error(f"MCP服务器运行失败: {e}")
        finally:
            self.server_running = False
            logger.info("MCP服务器已停止")
    
    def start(self):
        """启动MCP服务器"""
        if self.server_running:
            logger.warning("MCP服务器已经在运行")
            return
        
        # 启动服务器线程
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(1)
        self.server_running = True
        
        logger.info(f"MCP服务器已启动，可通过SSE连接到: http://localhost:{self.server_port}/sse")
    
    def stop(self):
        """停止MCP服务器"""
        if not self.server_running:
            logger.warning("MCP服务器未在运行")
            return
        
        # 注意：FastMCP目前没有提供优雅停止的方法
        # 由于服务器运行在独立线程中，当主程序退出时它会自动停止
        self.server_running = False
        logger.info("MCP服务器停止命令已发送")
    
    def is_running(self) -> bool:
        """检查MCP服务器是否在运行"""
        return self.server_running
    
    def set_game_logic(self, game_logic):
        """设置游戏逻辑实例
        
        Args:
            game_logic: 游戏逻辑实例
        """
        self.game_logic = game_logic
        self._register_tools()
        logger.info("游戏逻辑已设置到MCP服务器")
    
    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "running": self.server_running,
            "port": self.server_port,
            "url": f"http://localhost:{self.server_port}/sse" if self.server_running else None
        }