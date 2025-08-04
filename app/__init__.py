"""
现代化后台管理系统

基于 Dash + Flask 的企业级后台管理系统
支持用户认证、权限管理、数据管理等功能
"""

__version__ = "1.0.0"
__author__ = "Admin System Team"

import os
from flask import Flask
from dash import Dash
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """应用工厂函数"""
    from app.config import config
    from app.core.extensions import init_extensions
    
    # 自动检测配置环境
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # 创建 Flask 应用
    server = Flask(__name__)
    
    # 加载配置
    config_class = config.get(config_name, config['default'])
    server.config.from_object(config_class)
    
    # 先加载环境变量和统一配置
    from app.core.config_manager import config_manager
    
    # 从配置管理器获取各种配置
    jwt_config = config_manager.get_jwt_config()
    security_config = config_manager.get_security_config()
    
    # 更新Flask配置
    server.config.update(jwt_config)
    server.config.update(security_config)
    
    # 初始化配置
    config_class.init_app(server)
    
    # 创建 Dash 应用
    app = Dash(
        __name__,
        server=server,
        title=server.config.get('APP_TITLE', '现代化后台管理系统'),
        suppress_callback_exceptions=True,
        compress=True,
        update_title=None,
        external_stylesheets=[
            'https://cdn.jsdelivr.net/npm/antd@5.0.0/dist/reset.css'
        ]
    )
    
    # 初始化其他扩展
    init_extensions(app, server)
    
    # 注册蓝图和回调
    try:
        from app.views import register_layouts
        from app.callbacks import register_callbacks
        from app.api import register_api_blueprints
        
        register_layouts(app)
        register_callbacks(app)
        register_api_blueprints(server)
    except ImportError as e:
        logger.warning(f"部分模块尚未实现: {e}")
    
    logger.info(f"应用创建成功，配置: {config_name}")
    
    return app, server