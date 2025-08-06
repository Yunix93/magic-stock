"""
API接口模块

提供RESTful API接口
"""

from flask import Blueprint

def register_api_blueprints(app):
    """注册所有API蓝图"""
    # TODO: 实现API蓝图
    # 暂时注释掉不存在的导入，避免启动错误
    
    # from .auth import auth_bp
    # from .users import users_bp
    # from .roles import roles_bp
    # from .system import system_bp
    
    # 创建API主蓝图
    api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
    
    # TODO: 当子蓝图实现后，取消注释以下代码
    # api_bp.register_blueprint(auth_bp, url_prefix='/auth')
    # api_bp.register_blueprint(users_bp, url_prefix='/users')
    # api_bp.register_blueprint(roles_bp, url_prefix='/roles')
    # api_bp.register_blueprint(system_bp, url_prefix='/system')
    
    # 注册到应用
    app.register_blueprint(api_bp)
    
    print("⚠️  API蓝图尚未实现，请稍后添加具体的API端点")

__all__ = ['register_api_blueprints']