"""
认证相关的回调函数

处理登录、登出、注册等认证相关的回调
"""

from dash import Input, Output, State, callback, html, dcc, no_update
from dash.exceptions import PreventUpdate
import logging

logger = logging.getLogger(__name__)


def register_auth_callbacks(app):
    """注册认证相关的回调函数"""
    
    # 注册登录回调
    register_login_callback(app)
    
    # 注册登出回调
    register_logout_callback(app)
    
    logger.info("认证回调函数注册完成")


def register_login_callback(app):
    """注册登录回调"""
    
    @app.callback(
        [Output('login-error', 'children'),
         Output('login-error', 'className'),
         Output('login-success', 'children'),
         Output('login-success', 'className'),
         Output('user-session', 'data', allow_duplicate=True),
         Output('url', 'pathname')],
        [Input('login-submit', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value'),
         State('remember-me', 'value')],
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password, remember_me):
        """处理登录请求"""

        if not n_clicks:
            raise PreventUpdate
        
        try:
            # 验证输入
            if not username or not password:
                return (
                    "请输入用户名和密码",
                    "error-message show",
                    "",
                    "success-message",
                    no_update,
                    no_update
                )
            
            # 调用认证服务
            from app.services.auth_service import auth_service
            from app.core.exceptions import AuthenticationError
            
            try:
                # 认证用户
                auth_result = auth_service.authenticate_user(username, password)
                
                # 认证成功，创建用户会话数据
                user_data = auth_result['user']
                
                # 获取用户权限
                permissions = []
                if user_data.get('is_superuser', False):
                    # 超级用户拥有所有权限
                    permissions = [
                        'dashboard.view', 'user.view', 'user.create', 'user.update', 'user.delete',
                        'role.view', 'role.create', 'role.update', 'role.delete',
                        'permission.view', 'permission.assign',
                        'system.manage', 'system.monitor', 'system.config',
                        'log.view', 'log.export'
                    ]
                else:
                    # TODO: 从数据库获取用户实际权限
                    permissions = ['dashboard.view']  # 默认权限
                
                user_session = {
                    'user_id': user_data['id'],
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'full_name': user_data.get('full_name', ''),
                    'is_superuser': user_data.get('is_superuser', False),
                    'access_token': auth_result['access_token'],
                    'refresh_token': auth_result['refresh_token'],
                    'session_id': auth_result['session_id'],
                    'permissions': permissions
                }
                
                # TODO: 这里需要设置会话数据，暂时通过URL跳转
                return (
                    "",
                    "error-message",
                    "登录成功，正在跳转...",
                    "success-message show",
                    user_session,  # 设置会话数据
                    "/dashboard"  # 跳转到仪表板
                )
                
            except AuthenticationError as e:
                return (
                    str(e),
                    "error-message show",
                    "",
                    "success-message",
                    no_update,
                    no_update
                )
                
        except Exception as e:
            logger.error(f"登录处理异常: {e}")
            return (
                "登录失败，请稍后重试",
                "error-message show",
                "",
                "success-message",
                no_update,
                no_update
            )


def register_logout_callback(app):
    """注册登出回调"""
    
    @app.callback(
        [Output('user-session', 'data', allow_duplicate=True),
         Output('url', 'pathname', allow_duplicate=True)],
        [Input('logout-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def handle_logout(n_clicks):
        """处理登出请求"""
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # 清除会话数据
            return None, "/login"
            
        except Exception as e:
            logger.error(f"登出处理异常: {e}")
            return no_update, no_update


# 客户端回调用于设置会话数据
def register_clientside_callbacks(app):
    """注册客户端回调"""
    
    # 设置用户会话数据的客户端回调
    app.clientside_callback(
        """
        function(success_message, access_token, user_data) {
            if (success_message && success_message.includes('登录成功')) {
                // 设置会话数据
                return user_data;
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('user-session', 'data'),
        [Input('login-success', 'children'),
         State('login-success', 'className')],
        prevent_initial_call=True
    )


# 调试回调 - 监控会话数据变化
# 调试代码已移除


# 注册所有认证相关的回调
def register_all_auth_callbacks(app):
    """注册所有认证相关的回调函数"""
    register_auth_callbacks(app)
    register_clientside_callbacks(app)
# register_debug_callbacks(app)  # 调试代码已移除
    
    logger.info("所有认证回调函数注册完成")