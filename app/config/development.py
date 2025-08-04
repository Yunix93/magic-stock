"""
开发环境配置

用于本地开发和调试
"""

import os
from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """开发环境配置类"""
    
    # 调试模式
    DEBUG = True
    TESTING = False
    
    # 开发环境数据库
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL', 
        'sqlite:///dev_admin_system.db'
    )
    
    # 开发环境Redis
    REDIS_URL = os.getenv('DEV_REDIS_URL', 'redis://localhost:6379/1')
    
    # 日志配置
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/dev_app.log'
    
    # 开发环境邮件配置（使用控制台输出）
    MAIL_SUPPRESS_SEND = True
    MAIL_DEBUG = True
    
    # 安全配置（开发环境放宽）
    SESSION_COOKIE_SECURE = False
    JWT_ACCESS_TOKEN_EXPIRES = BaseConfig.JWT_ACCESS_TOKEN_EXPIRES * 2  # 延长开发环境token有效期
    
    # 开发工具
    FLASK_DEBUG_TOOLBAR = True
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # 热重载配置
    DASH_HOT_RELOAD = True
    DASH_DEV_TOOLS = True
    
    # 开发环境允许的主机
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
    
    # 跨域配置（开发环境允许）
    API_ENABLE_CORS = True
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # 缓存配置（开发环境使用简单缓存）
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60  # 短缓存时间便于调试
    
    # 文件上传配置
    UPLOAD_FOLDER = 'dev_uploads'
    
    # 密码策略（开发环境放宽）
    PASSWORD_MIN_LENGTH = 6
    PASSWORD_REQUIRE_UPPERCASE = False
    PASSWORD_REQUIRE_SYMBOLS = False
    
    # 登录安全（开发环境放宽）
    MAX_LOGIN_ATTEMPTS = 10
    LOGIN_LOCKOUT_DURATION = 300  # 5分钟
    
    # API限制（开发环境放宽）
    API_RATE_LIMIT = '1000/hour'
    
    @staticmethod
    def init_app(app):
        """初始化开发环境应用配置"""
        BaseConfig.init_app(app)
        
        # 创建开发环境特定目录
        os.makedirs('dev_uploads', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # 开发环境日志配置
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        print("🔧 开发环境配置已加载")
        print(f"📊 数据库: {DevelopmentConfig.SQLALCHEMY_DATABASE_URI}")
        print(f"🔄 Redis: {DevelopmentConfig.REDIS_URL}")
        print(f"📝 日志级别: {DevelopmentConfig.LOG_LEVEL}")
        print(f"🔐 调试模式: {DevelopmentConfig.DEBUG}")