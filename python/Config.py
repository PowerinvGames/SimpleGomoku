"""
配置管理类
集中管理所有可配置项，包括界面颜色、尺寸、文本等
"""
import os
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置，优先从配置文件读取，没有则使用默认配置"""
        # 这里可以添加从配置文件读取的逻辑
        # 例如从resources/config.properties读取
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  "resources", "config.properties")
        
        if os.path.exists(config_file):
            try:
                self._load_from_properties(config_file)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def _load_from_properties(self, filepath: str):
        """从properties文件加载配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().encode('utf-8').decode('unicode_escape')
                        
                        # 尝试转换为适当类型
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        elif self._is_float(value):
                            value = float(value)
                        elif value.startswith('(') and value.endswith(')'):
                            # 处理元组格式的颜色值，如 (255, 255, 255)
                            try:
                                value = tuple(map(int, value[1:-1].split(',')))
                            except:
                                pass
                        
                        self._config[key] = value
    
    def _is_float(self, value: str) -> bool:
        """检查字符串是否可以转换为浮点数"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
    
    def save_to_file(self, filepath: str = None):
        """保存配置到文件"""
        if filepath is None:
            filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   "resources", "config.properties")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# 五子棋游戏配置\n")
                f.write("# 自动生成，请勿手动修改\n\n")
                
                for key, value in self._config.items():
                    if isinstance(value, tuple):
                        f.write(f"{key}=({','.join(map(str, value))})\n")
                    else:
                        f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"保存配置文件失败: {e}")


# 全局配置实例
config = Config()