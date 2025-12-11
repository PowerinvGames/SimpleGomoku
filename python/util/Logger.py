"""
日志管理器
提供统一的日志记录接口，类似log4j的用法
"""
import logging
import sys
from typing import Optional


class Logger:
    """日志管理器类"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志器"""
        # 创建logger
        self._logger = logging.getLogger("Gomoku")
        self._logger.setLevel(logging.DEBUG)
        
        # 清除已有的handler，避免重复
        self._logger.handlers.clear()
        
        # 创建控制台handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # 设置编码为UTF-8
        console_handler.setStream(sys.stdout)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # 添加handler到logger
        self._logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """获取日志器实例"""
        return self._logger
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self._logger.critical(message, *args, **kwargs)


# 全局日志实例
logger = Logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取指定名称的日志器
    如果未指定名称，返回默认日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger实例
    """
    if name:
        return logging.getLogger(name)
    return logger.get_logger()