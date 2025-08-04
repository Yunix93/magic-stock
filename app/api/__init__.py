"""
API接口模块

提供RESTful API接口
"""

from flask import Blueprint

def register_api_blueprints(app):
    """注册所有API蓝图"""
    from .auth import auth_bp
    from .users import users_bp
    from .roles import roles_bp
    from .system import system_bp
    
    # 创建API主蓝图
    api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
    
    # 注册子蓝图
    api_bp.register_blueprint(auth_bp, url_prefix='/auth')
    api_bp.register_blueprint(users_bp, url_prefix='/users')
    api_bp.register_blueprint(roles_bp, url_prefix='/roles')
    api_bp.register_blueprint(system_bp, url_prefix='/system')
    
    # 注册到应用
    app.register_blueprint(api_bp)

__all__ = ['register_api_blueprints']