"""
扩展初始化模块

初始化所有Flask和Dash扩展
"""

from flask_login import LoginManager
from flask_principal import Principal
from flask_caching import Cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis
import logging
import os

# 全局扩展实例
login_manager = LoginManager()
principal = Principal()
cache = Cache()
logger = logging.getLogger(__name__)

# Redis客户端
redis_client = None


def init_extensions(app, server):
    """初始化所有扩展"""
    
    # 初始化登录管理器
    init_login_manager(server)
    
    # 初始化权限管理器
    init_principal(server)
    
    # 初始化缓存
    init_cache(server)
    
    # 初始化数据库
    init_database(server)
    
    # 初始化Redis
    init_redis(server)
    
    # 初始化日志
    init_logging(server)
    
    logger.info("所有扩展初始化完成")




def init_login_manager(server):
    """初始化登录管理器"""
    login_manager.init_app(server)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    @login_manager.user_loader
    def load_user(user_id):
        """用户加载回调"""
        from app.models.user import User
        return User.query.get(user_id)
    
    @login_manager.unauthorized_handler
    def unauthorized():
        """未授权处理"""
        from flask import redirect, url_for, request, flash
        flash('请先登录以访问此页面', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    logger.info("登录管理器初始化完成")


def init_principal(server):
    """初始化权限管理器"""
    principal.init_app(server)
    
    from flask_principal import identity_loaded, UserNeed, RoleNeed
    from flask_login import current_user
    
    @identity_loaded.connect_via(server)
    def on_identity_loaded(sender, identity):
        """身份加载回调"""
        identity.user = current_user
        
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))
        
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))
                
                # 添加角色权限
                for permission in role.permissions:
                    identity.provides.add(permission.to_need())
    
    logger.info("权限管理器初始化完成")


def init_cache(server):
    """初始化缓存"""
    cache.init_app(server)
    logger.info(f"缓存初始化完成，类型: {server.config.get('CACHE_TYPE', 'simple')}")


def init_database(server):
    """初始化数据库"""
    from app.core.database import init_database as core_init_database
    from app.core.config_manager import config_manager
    
    try:
        # 从配置管理器获取数据库配置
        db_config = config_manager.get_database_config()
        
        # 更新Flask配置
        server.config.update(db_config)
        
        # 初始化数据库连接
        engine, session_factory = core_init_database()
        
        
        logger.info("数据库初始化完成")
        return engine, session_factory
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def init_redis(server):
    """初始化Redis"""
    from app.core.config_manager import config_manager
    global redis_client
    
    redis_url = config_manager.get_redis_config()
    if redis_url:
        try:
            redis_client = redis.from_url(redis_url)
            # 测试Redis连接
            redis_client.ping()
            logger.info(f"Redis连接成功: {redis_url}")
            server.config['REDIS_URL'] = redis_url
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            redis_client = None
    else:
        logger.info("未配置Redis，跳过初始化")


def init_logging(server):
    """初始化日志系统"""
    from app.core.config_manager import config_manager
    
    # 从配置管理器获取日志配置
    log_config = config_manager.get_logging_config()
    
    # 更新Flask配置
    server.config.update(log_config)
    
    log_level = log_config['LOG_LEVEL']
    log_file = log_config['LOG_FILE']
    
    # 设置日志级别
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(numeric_level)
    
    # 配置日志格式
    formatter = logging.Formatter(log_config['LOG_FORMAT'])
    
    # 配置文件日志处理器
    if log_file and not server.config.get('TESTING'):
        from logging.handlers import RotatingFileHandler
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=server.config.get('LOG_MAX_BYTES', 10485760),
            backupCount=server.config.get('LOG_BACKUP_COUNT', 5)
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        
        # 添加到应用日志
        server.logger.addHandler(file_handler)
        logging.getLogger().addHandler(file_handler)
    
    # 配置控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    
    # 避免重复添加处理器
    if not server.logger.handlers:
        server.logger.addHandler(console_handler)
    
    logger.info(f"日志系统初始化完成，级别: {log_level}")


def get_db_session():
    """获取数据库会话"""
    from app.core.database import get_session
    return get_session()


def get_redis_client():
    """获取Redis客户端"""
    return redis_client