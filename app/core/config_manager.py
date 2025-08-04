"""
统一配置管理器

提供统一的配置加载和管理功能
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _config_loaded = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if not self._config_loaded:
            self.load_environment_variables()
            self._config_loaded = True
    
    def load_environment_variables(self):
        """加载环境变量"""
        # 按优先级加载环境变量文件
        env_files = ['.env.local', '.env', '.env.example']
        
        for env_file in env_files:
            if os.path.exists(env_file):
                load_dotenv(env_file)
                logger.info(f"已加载环境变量文件: {env_file}")
                break
        else:
            logger.warning("未找到环境变量文件，使用默认配置")
    
    def get_database_config(self, config_name: str = None) -> Dict[str, Any]:
        """获取数据库配置"""
        config_name = config_name or os.getenv('FLASK_ENV', 'development')
        
        # 基础配置
        base_config = {
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_RECORD_QUERIES': True,
            'SQLALCHEMY_ENGINE_OPTIONS': {}
        }
        
        # 根据环境获取数据库URL
        if config_name == 'testing':
            database_url = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
        elif config_name == 'production':
            database_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
        else:  # development
            database_url = os.getenv('DEV_DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///dev_admin_system.db')
        
        if not database_url:
            raise ValueError(f"未配置 {config_name} 环境的数据库连接URL")
        
        base_config['SQLALCHEMY_DATABASE_URI'] = database_url
        
        # 根据数据库类型调整引擎配置
        if database_url.startswith('sqlite'):
            base_config['SQLALCHEMY_ENGINE_OPTIONS'].update({
                'pool_pre_ping': False,
                'pool_recycle': -1,
                'connect_args': {'check_same_thread': False}
            })
        elif database_url.startswith('postgresql'):
            base_config['SQLALCHEMY_ENGINE_OPTIONS'].update({
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'pool_size': 10,
                'max_overflow': 20
            })
        elif database_url.startswith('mysql'):
            base_config['SQLALCHEMY_ENGINE_OPTIONS'].update({
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'pool_size': 10,
                'max_overflow': 20,
                'connect_args': {'charset': 'utf8mb4'}
            })
        
        return base_config
    
    def get_redis_config(self) -> Optional[str]:
        """获取Redis配置"""
        return os.getenv('REDIS_URL')
    
    def get_jwt_config(self) -> Dict[str, Any]:
        """获取JWT配置"""
        return {
            'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
            'JWT_ACCESS_TOKEN_EXPIRES': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600')),
            'JWT_REFRESH_TOKEN_EXPIRES': int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '86400')),
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return {
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', 'logs/app.log'),
            'LOG_FORMAT': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'LOG_MAX_BYTES': int(os.getenv('LOG_MAX_BYTES', '10485760')),  # 10MB
            'LOG_BACKUP_COUNT': int(os.getenv('LOG_BACKUP_COUNT', '5')),
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return {
            'MAX_LOGIN_ATTEMPTS': int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
            'LOCKOUT_DURATION': int(os.getenv('LOCKOUT_DURATION', '900')),  # 15分钟
            'SESSION_TIMEOUT': int(os.getenv('SESSION_TIMEOUT', '86400')),  # 24小时
            'PASSWORD_MIN_LENGTH': int(os.getenv('PASSWORD_MIN_LENGTH', '8')),
            'PASSWORD_REQUIRE_UPPERCASE': os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true',
            'PASSWORD_REQUIRE_LOWERCASE': os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true',
            'PASSWORD_REQUIRE_NUMBERS': os.getenv('PASSWORD_REQUIRE_NUMBERS', 'true').lower() == 'true',
            'PASSWORD_REQUIRE_SYMBOLS': os.getenv('PASSWORD_REQUIRE_SYMBOLS', 'false').lower() == 'true',
        }


# 全局配置管理器实例
config_manager = ConfigManager()