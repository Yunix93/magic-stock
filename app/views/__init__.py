"""
视图模块

包含所有页面布局和组件
"""

def register_layouts(app):
    """注册所有页面布局"""
    # TODO: 实现页面布局
    # 暂时注释掉不存在的导入，避免启动错误
    
    # from .auth.login import register_login_layout
    # from .dashboard.main import register_dashboard_layout
    # from .users.management import register_user_management_layout
    # from .system.settings import register_system_settings_layout
    
    # TODO: 当页面布局实现后，取消注释以下代码
    # register_login_layout(app)
    # register_dashboard_layout(app)
    # register_user_management_layout(app)
    # register_system_settings_layout(app)
    
    print("⚠️  页面布局尚未实现，请稍后添加具体的页面组件")

__all__ = ['register_layouts']