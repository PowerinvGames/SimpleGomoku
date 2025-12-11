"""
端口查找工具类
用于检测空闲端口，避免端口冲突
"""
import socket
from typing import Optional

from python.util.Logger import logger


class PortFinder:
    """端口查找工具类"""
    
    @staticmethod
    def is_port_available(port: int, host: str = "localhost") -> bool:
        """
        检查指定端口是否可用
        
        Args:
            port: 要检查的端口号
            host: 主机地址，默认为localhost
            
        Returns:
            bool: 端口是否可用
        """
        try:
            # 创建socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # 设置超时时间
            
            # 尝试绑定端口
            sock.bind((host, port))
            sock.close()
            
            logger.debug(f"端口 {port} 可用")
            return True
        except socket.error as e:
            logger.debug(f"端口 {port} 不可用: {e}")
            return False
    
    @staticmethod
    def find_available_port(start_port: int = 60000, end_port: int = 65535, 
                           host: str = "localhost") -> Optional[int]:
        """
        在指定范围内查找可用的端口
        
        Args:
            start_port: 起始端口号，默认为60000
            end_port: 结束端口号，默认为65535
            host: 主机地址，默认为localhost
            
        Returns:
            Optional[int]: 找到的可用端口号，如果没找到则返回None
        """
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            logger.error(f"端口范围无效: {start_port}-{end_port}")
            return None
        
        logger.info(f"在范围 {start_port}-{end_port} 中查找可用端口...")
        
        for port in range(start_port, end_port + 1):
            if PortFinder.is_port_available(port, host):
                logger.info(f"找到可用端口: {port}")
                return port
        
        logger.warning(f"在范围 {start_port}-{end_port} 中未找到可用端口")
        return None
    
    @staticmethod
    def find_available_port_with_retry(start_port: int = 60000, end_port: int = 65535,
                                      host: str = "localhost", max_attempts: int = 3) -> Optional[int]:
        """
        查找可用端口，支持重试机制
        
        Args:
            start_port: 起始端口号
            end_port: 结束端口号
            host: 主机地址
            max_attempts: 最大尝试次数
            
        Returns:
            Optional[int]: 找到的可用端口号
        """
        for attempt in range(max_attempts):
            logger.info(f"尝试查找可用端口 (第 {attempt + 1}/{max_attempts} 次)...")
            
            port = PortFinder.find_available_port(start_port, end_port, host)
            if port is not None:
                return port
            
            # 如果没找到，可以尝试调整范围
            if attempt < max_attempts - 1:
                # 可以尝试不同的端口范围
                new_start = start_port + 1000  # 每次增加1000
                if new_start <= end_port:
                    start_port = new_start
                    logger.info(f"调整端口范围到: {start_port}-{end_port}")
        
        logger.error(f"经过 {max_attempts} 次尝试仍未找到可用端口")
        return None
    
    @staticmethod
    def get_suggested_port_range() -> tuple[int, int]:
        """
        获取建议的端口范围
        
        Returns:
            tuple[int, int]: (起始端口, 结束端口)
        """
        # 建议使用60000-65535范围，这是动态/私有端口范围
        return 60000, 65535