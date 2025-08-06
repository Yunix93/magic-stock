"""
回调函数模块

包含所有Dash回调函数
"""

from .layout_callbacks import register_all_layout_callbacks
from .auth_callbacks import register_all_auth_callbacks

def register_callbacks(app):
    """注册所有回调函数"""
    
    # 注册布局相关回调
    register_all_layout_callbacks(app)
    
    # 注册认证相关回调
    register_all_auth_callbacks(app)
    
    # TODO: 注册其他回调函数
    # from .user_callbacks import register_user_callbacks
    # from .system_callbacks import register_system_callbacks
    
    # register_user_callbacks(app)
    # register_system_callbacks(app)
    
    print("✅ 回调函数注册完成")

__all__ = ['register_callbacks']