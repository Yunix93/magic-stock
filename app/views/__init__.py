"""
视图模块

包含所有页面布局和组件
"""

def register_layouts(app):
    """注册所有页面布局"""
    from .auth.login import register_login_layout
    from .dashboard.main import register_dashboard_layout
    from .users.management import register_user_management_layout
    from .system.settings import register_system_settings_layout
    
    # 注册各个模块的布局
    register_login_layout(app)
    register_dashboard_layout(app)
    register_user_management_layout(app)
    register_system_settings_layout(app)

__all__ = ['register_layouts']