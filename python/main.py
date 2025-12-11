"""
程序入口点
启动五子棋游戏
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python.Logger import logger
from python.GameWindow import GameWindow


def main():
    """主函数"""
    try:
        logger.info("启动五子棋游戏...")
        
        # 创建并运行游戏窗口
        window = GameWindow()
        
        logger.info("游戏窗口创建成功，开始运行...")
        arcade.run()
        
        logger.info("游戏正常退出")
        
    except Exception as e:
        logger.error(f"游戏运行出错: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    # 检查arcade库是否安装
    try:
        import arcade
    except ImportError:
        print("错误: 未安装arcade库")
        print("请运行: pip install arcade")
        sys.exit(1)
    
    # 运行游戏
    exit_code = main()
    sys.exit(exit_code)