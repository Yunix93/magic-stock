"""
回调函数模块

包含所有Dash回调函数
"""

def register_callbacks(app):
    """注册所有回调函数"""
    from .auth_callbacks import register_auth_callbacks
    from .user_callbacks import register_user_callbacks
    from .system_callbacks import register_system_callbacks
    
    # 注册各个模块的回调函数
    register_auth_callbacks(app)
    register_user_callbacks(app)
    register_system_callbacks(app)

__all__ = ['register_callbacks']