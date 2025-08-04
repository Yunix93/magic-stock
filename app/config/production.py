"""
生产环境配置

用于生产部署
"""

import os
from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """生产环境配置类"""
    
    # 生产模式
    DEBUG = False
    TESTING = False
    
    # 生产环境数据库（必须通过环境变量配置）
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # 生产环境Redis（必须通过环境变量配置）
    REDIS_URL = os.getenv('REDIS_URL')
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    LOG_FILE = '/var/log/admin_system/app.log'
    
    # 数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_timeout': 30,
        'max_overflow': 20,
        'pool_size': 10
    }
    
    # 缓存配置
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 3600  # 1小时
    
    # 文件上传配置
    UPLOAD_FOLDER = '/var/uploads/admin_system'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    
    # 邮件配置（生产环境必须配置）
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # 安全策略（生产环境严格）
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SYMBOLS = True
    
    # 登录安全
    MAX_LOGIN_ATTEMPTS = 3
    LOGIN_LOCKOUT_DURATION = 1800  # 30分钟
    
    # API限制
    API_RATE_LIMIT = '60/hour'
    
    # 监控配置
    ENABLE_METRICS = True
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    
    # 浏览器检查
    STRICT_BROWSER_CHECK = True
    
    # HTTPS配置
    PREFERRED_URL_SCHEME = 'https'
    
    # 内容安全策略
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' cdn.jsdelivr.net",
        'img-src': "'self' data: cdn.jsdelivr.net",
        'font-src': "'self' cdn.jsdelivr.net",
        'connect-src': "'self'",
        'frame-ancestors': "'none'"
    }
    
    @staticmethod
    def init_app(app):
        """初始化生产环境应用配置"""
        # 生产环境必要配置检查
        if not ProductionConfig.SQLALCHEMY_DATABASE_URI:
            raise ValueError("生产环境必须设置 DATABASE_URL 环境变量")
        
        if not ProductionConfig.REDIS_URL:
            raise ValueError("生产环境必须设置 REDIS_URL 环境变量")
        
        if not ProductionConfig.SECRET_KEY or ProductionConfig.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("生产环境必须设置安全的 SECRET_KEY")
        
        BaseConfig.init_app(app)
        
        # 创建生产环境目录
        os.makedirs('/var/log/admin_system', exist_ok=True)
        os.makedirs('/var/uploads/admin_system', exist_ok=True)
        
        # 生产环境日志配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        # 配置文件日志
        file_handler = RotatingFileHandler(
            ProductionConfig.LOG_FILE,
            maxBytes=ProductionConfig.LOG_MAX_BYTES,
            backupCount=ProductionConfig.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(ProductionConfig.LOG_FORMAT))
        file_handler.setLevel(logging.WARNING)
        
        # 配置错误日志
        error_handler = RotatingFileHandler(
            '/var/log/admin_system/error.log',
            maxBytes=ProductionConfig.LOG_MAX_BYTES,
            backupCount=ProductionConfig.LOG_BACKUP_COUNT
        )
        error_handler.setFormatter(logging.Formatter(ProductionConfig.LOG_FORMAT))
        error_handler.setLevel(logging.ERROR)
        
        # 添加到应用日志
        app.server.logger.addHandler(file_handler)
        app.server.logger.addHandler(error_handler)
        app.server.logger.setLevel(logging.WARNING)
        
        # 配置Sentry错误监控
        if ProductionConfig.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_sdk.init(
                dsn=ProductionConfig.SENTRY_DSN,
                integrations=[
                    FlaskIntegration(),
                    SqlalchemyIntegration()
                ],
                traces_sample_rate=0.1,
                environment='production'
            )
        
        print("🚀 生产环境配置已加载")
        print(f"🔒 安全模式: 已启用")
        print(f"📊 监控: {'已启用' if ProductionConfig.ENABLE_METRICS else '未启用'}")
        print(f"📧 邮件: {'已配置' if ProductionConfig.MAIL_SERVER else '未配置'}")