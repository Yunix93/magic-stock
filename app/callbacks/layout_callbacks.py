"""
布局相关的回调函数

处理导航、菜单、用户交互等布局相关的回调
"""

from dash import Input, Output, State, callback, html, dcc, no_update
from dash.exceptions import PreventUpdate
import logging

logger = logging.getLogger(__name__)


def register_layout_callbacks(app):
    """注册布局相关的回调函数"""
    
    # 注册面包屑更新回调
    register_breadcrumb_callback(app)
    
    # 注册侧边栏菜单回调
    register_sidebar_callbacks(app)
    
    # 注册用户下拉菜单回调
    register_user_dropdown_callbacks(app)
    
    # 注册移动端菜单回调
    register_mobile_menu_callbacks(app)
    
    logger.info("布局回调函数注册完成")


def register_breadcrumb_callback(app):
    """注册面包屑导航更新回调"""
    
    @app.callback(
        Output('current-page-breadcrumb', 'children'),
        [Input('url', 'pathname')],
        prevent_initial_call=True
    )
    def update_breadcrumb(pathname):
        """更新面包屑导航"""
        try:
            # 路径到页面名称的映射
            path_names = {
                '/': '首页',
                '/dashboard': '仪表板',
                '/users': '用户管理',
                '/users/list': '用户列表',
                '/users/add': '添加用户',
                '/roles': '角色权限',
                '/roles/list': '角色管理',
                '/permissions': '权限管理',
                '/monitor': '系统监控',
                '/monitor/status': '系统状态',
                '/monitor/logs': '操作日志',
                '/system': '系统设置',
                '/system/basic': '基础设置',
                '/system/security': '安全设置',
                '/profile': '个人资料',
                '/settings': '账户设置',
                '/login': '用户登录'
            }
            
            return path_names.get(pathname, '未知页面')
            
        except Exception as e:
            logger.error(f"更新面包屑导航异常: {e}")
            return '页面'


def register_sidebar_callbacks(app):
    """注册侧边栏菜单回调"""
    
    # 侧边栏菜单更新暂时注释掉，因为菜单是在布局中静态生成的
    # 如果需要动态更新菜单，可以取消注释并实现相应的逻辑
    # @app.callback(
    #     Output('sidebar-menu', 'children'),
    #     [Input('user-session', 'data'),
    #      Input('url', 'pathname')],
    #     prevent_initial_call=True
    # )
    # def update_sidebar_menu(user_session, pathname):
    #     """更新侧边栏菜单状态"""
    #     try:
    #         if not user_session or not user_session.get('user_id'):
    #             return no_update
    #         
    #         # 这里可以根据当前路径高亮对应的菜单项
    #         # 实际实现需要根据具体的菜单结构来处理
    #         return no_update
    #         
    #     except Exception as e:
    #         logger.error(f"更新侧边栏菜单异常: {e}")
    #         return no_update


def register_user_dropdown_callbacks(app):
    """注册用户下拉菜单回调"""
    
    # 这里可以添加用户下拉菜单的交互逻辑
    # 由于Dash的限制，复杂的下拉菜单交互可能需要通过JavaScript实现
    pass


def register_mobile_menu_callbacks(app):
    """注册移动端菜单回调"""
    
    # 这里可以添加移动端菜单的显示/隐藏逻辑
    # 同样可能需要通过JavaScript实现
    pass


# 页面标题更新已经在路由管理器中处理，这里不需要重复的回调


# 全局状态管理回调
def register_global_state_callbacks(app):
    """注册全局状态管理回调"""
    
    @app.callback(
        Output('global-state', 'data'),
        [Input('user-session', 'data')],
        [State('global-state', 'data')],
        prevent_initial_call=True
    )
    def update_global_state(user_session, current_state):
        """更新全局状态"""
        try:
            if current_state is None:
                current_state = {}
            
            # 更新用户相关的全局状态
            if user_session:
                current_state.update({
                    'is_authenticated': bool(user_session.get('user_id')),
                    'user_permissions': user_session.get('permissions', []),
                    'user_role': user_session.get('role', 'guest')
                })
            else:
                current_state.update({
                    'is_authenticated': False,
                    'user_permissions': [],
                    'user_role': 'guest'
                })
            
            return current_state
            
        except Exception as e:
            logger.error(f"更新全局状态异常: {e}")
            return current_state or {}


# 注册所有布局相关的回调
def register_all_layout_callbacks(app):
    """注册所有布局相关的回调函数"""
    register_layout_callbacks(app)
    register_global_state_callbacks(app)
    
    logger.info("所有布局回调函数注册完成")