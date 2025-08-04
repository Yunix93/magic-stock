"""
测试环境配置

用于单元测试和集成测试
"""

import os
import tempfile
from .base import BaseConfig


class TestingConfig(BaseConfig):
    """测试环境配置类"""
    
    # 测试模式
    DEBUG = False
    TESTING = True
    
    # 测试数据库（使用内存数据库）
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    
    # 测试环境Redis（使用fake redis）
    CACHE_TYPE = 'simple'
    REDIS_URL = None
    
    # 安全配置（测试环境使用固定值）
    SECRET_KEY = 'test-secret-key-for-testing-only'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    WTF_CSRF_ENABLED = False  # 测试时禁用CSRF
    
    # 会话配置
    SESSION_COOKIE_SECURE = False
    
    # 日志配置（测试时最小化日志）
    LOG_LEVEL = 'ERROR'
    LOG_FILE = None  # 不写入文件
    
    # 邮件配置（测试时不发送邮件）
    MAIL_SUPPRESS_SEND = True
    MAIL_DEBUG = False
    
    # 文件上传配置（使用临时目录）
    UPLOAD_FOLDER = tempfile.mkdtemp()
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB
    
    # 密码策略（测试环境简化）
    PASSWORD_MIN_LENGTH = 4
    PASSWORD_REQUIRE_UPPERCASE = False
    PASSWORD_REQUIRE_LOWERCASE = False
    PASSWORD_REQUIRE_NUMBERS = False
    PASSWORD_REQUIRE_SYMBOLS = False
    
    # 登录安全（测试环境放宽）
    MAX_LOGIN_ATTEMPTS = 100
    LOGIN_LOCKOUT_DURATION = 1  # 1秒
    
    # API限制（测试环境不限制）
    API_RATE_LIMIT = '10000/hour'
    
    # 缓存配置（测试环境不缓存）
    CACHE_DEFAULT_TIMEOUT = 1
    
    # 浏览器检查（测试环境跳过）
    STRICT_BROWSER_CHECK = False
    
    # 测试数据库配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': False,
        'pool_recycle': -1,
        'echo': False
    }
    
    # 禁用监控
    ENABLE_METRICS = False
    SENTRY_DSN = None
    
    @staticmethod
    def init_app(app):
        """初始化测试环境应用配置"""
        # 不调用BaseConfig.init_app，避免创建目录
        
        # 测试环境日志配置（只输出到控制台）
        import logging
        logging.basicConfig(
            level=logging.ERROR,
            format='%(levelname)s - %(message)s'
        )
        
        # 禁用Flask日志（app参数是Flask实例）
        app.logger.setLevel(logging.ERROR)
        
        print("🧪 测试环境配置已加载")
        print(f"💾 数据库: 内存数据库")
        print(f"📝 日志级别: ERROR")
        print(f"🔐 CSRF保护: 已禁用")
    
    @staticmethod
    def cleanup():
        """清理测试环境资源"""
        import shutil
        if os.path.exists(TestingConfig.UPLOAD_FOLDER):
            shutil.rmtree(TestingConfig.UPLOAD_FOLDER, ignore_errors=True)