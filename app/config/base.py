"""
基础配置类

包含所有环境共用的基础配置
"""

import os
from datetime import timedelta
from typing import List, Dict, Any


class BaseConfig:
    """基础配置类"""
    
    # 应用基础信息
    APP_TITLE = os.getenv('APP_TITLE', '现代化后台管理系统')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    APP_DESCRIPTION = os.getenv('APP_DESCRIPTION', '基于Dash的企业级后台管理系统')
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '24')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '30')))
    
    # 会话配置
    SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME', 'admin_session')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv('PERMANENT_SESSION_LIFETIME', '24')))
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///admin_system.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Redis配置
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis' if REDIS_URL else 'simple'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # 分页配置
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '20'))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '100'))
    
    # 文件上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'csv'}
    
    # 邮件配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'admin@example.com')
    
    # 安全策略
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_NUMBERS = os.getenv('PASSWORD_REQUIRE_NUMBERS', 'True').lower() == 'true'
    PASSWORD_REQUIRE_SYMBOLS = os.getenv('PASSWORD_REQUIRE_SYMBOLS', 'False').lower() == 'true'
    
    # 登录安全
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    LOGIN_LOCKOUT_DURATION = int(os.getenv('LOGIN_LOCKOUT_DURATION', '900'))  # 15分钟
    
    # API配置
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100/hour')
    API_ENABLE_CORS = os.getenv('API_ENABLE_CORS', 'True').lower() == 'true'
    
    # 监控配置
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'False').lower() == 'true'
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    
    # 浏览器支持配置
    MIN_BROWSER_VERSIONS = {
        'Chrome': 88,
        'Firefox': 78,
        'Edge': 100,
        'Safari': 14
    }
    STRICT_BROWSER_CHECK = os.getenv('STRICT_BROWSER_CHECK', 'False').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的目录
        os.makedirs('logs', exist_ok=True)
        os.makedirs(BaseConfig.UPLOAD_FOLDER, exist_ok=True)
        
        # 验证必要的配置
        BaseConfig.validate_config()
    
    @staticmethod
    def validate_config():
        """验证配置有效性"""
        errors = []
        
        # 检查必要的环境变量
        required_vars = ['SECRET_KEY']
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"缺少必要的环境变量: {var}")
        
        # 检查数据库URL格式
        database_url = os.getenv('DATABASE_URL')
        if database_url and not any(database_url.startswith(prefix) for prefix in ['sqlite:', 'postgresql:', 'mysql:']):
            errors.append("DATABASE_URL 格式不正确")
        
        if errors:
            raise ValueError("配置验证失败:\n" + "\n".join(errors))
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """获取配置字典"""
        config_dict = {}
        for key in dir(cls):
            if key.isupper() and not key.startswith('_'):
                config_dict[key] = getattr(cls, key)
        return config_dict