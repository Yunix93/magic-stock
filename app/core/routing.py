"""
路由管理器

提供Dash应用的路由管理功能
"""

import logging
from typing import Dict, List, Callable, Optional, Any
from urllib.parse import urlparse, parse_qs
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

logger = logging.getLogger(__name__)


class RouteManager:
    """路由管理器"""
    
    def __init__(self, app):
        """
        初始化路由管理器
        
        Args:
            app: Dash应用实例
        """
        self.app = app
        self.routes = {}
        self.middleware = []
        self.error_handlers = {}
        self.default_layout = None
        
        # 注册默认路由回调
        self._register_routing_callback()
        
        logger.info("路由管理器初始化完成")
    
    def register_route(self, path: str, layout_func: Callable, 
                      title: str = None, permissions: List[str] = None,
                      middleware: List[Callable] = None):
        """
        注册路由
        
        Args:
            path: 路由路径
            layout_func: 布局函数
            title: 页面标题
            permissions: 所需权限列表
            middleware: 中间件列表
        """
        self.routes[path] = {
            'layout_func': layout_func,
            'title': title or '现代化后台管理系统',
            'permissions': permissions or [],
            'middleware': middleware or []
        }
        
        logger.info(f"注册路由: {path}")
    
    def register_middleware(self, middleware_func: Callable):
        """
        注册全局中间件
        
        Args:
            middleware_func: 中间件函数
        """
        self.middleware.append(middleware_func)
        logger.info(f"注册全局中间件: {middleware_func.__name__}")
    
    def register_error_handler(self, error_code: int, handler_func: Callable):
        """
        注册错误处理器
        
        Args:
            error_code: 错误代码
            handler_func: 处理函数
        """
        self.error_handlers[error_code] = handler_func
        logger.info(f"注册错误处理器: {error_code}")
    
    def set_default_layout(self, layout_func: Callable):
        """
        设置默认布局
        
        Args:
            layout_func: 默认布局函数
        """
        self.default_layout = layout_func
        logger.info("设置默认布局")
    
    def _register_routing_callback(self):
        """注册路由回调函数"""
        
        @self.app.callback(
            [Output('page-content', 'children'),
             Output('page-title', 'data')],
            [Input('url', 'pathname'),
             Input('url', 'search')],
            [State('user-session', 'data')]
        )
        def route_callback(pathname, search, user_session):
            """路由回调函数"""
            try:
                return self._handle_route(pathname, search, user_session)
            except Exception as e:
                logger.error(f"路由处理异常: {e}")
                return self._handle_error(500, str(e))
    
    def _handle_route(self, pathname: str, search: str, user_session: dict):
        """
        处理路由
        
        Args:
            pathname: 路径名
            search: 查询参数
            user_session: 用户会话数据
            
        Returns:
            tuple: (页面内容, 页面标题)
        """
        # 解析查询参数
        query_params = parse_qs(search.lstrip('?')) if search else {}
        
        # 构建请求上下文
        request_context = {
            'pathname': pathname,
            'search': search,
            'query_params': query_params,
            'user_session': user_session or {}
        }
        
        # 执行全局中间件
        for middleware in self.middleware:
            try:
                result = middleware(request_context)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"中间件执行异常: {e}")
                return self._handle_error(500, f"中间件错误: {str(e)}")
        
        # 查找匹配的路由
        route_config = self._find_route(pathname)
        
        if not route_config:
            return self._handle_error(404, f"页面不存在: {pathname}")
        
        # 检查权限
        if not self._check_permissions(route_config['permissions'], user_session):
            return self._handle_error(403, "权限不足")
        
        # 执行路由中间件
        for middleware in route_config['middleware']:
            try:
                result = middleware(request_context)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"路由中间件执行异常: {e}")
                return self._handle_error(500, f"路由中间件错误: {str(e)}")
        
        # 生成页面内容
        try:
            layout_func = route_config['layout_func']
            page_content = layout_func(request_context)
            page_title = route_config['title']
            
            return page_content, page_title
            
        except Exception as e:
            logger.error(f"页面生成异常: {e}")
            return self._handle_error(500, f"页面生成错误: {str(e)}")
    
    def _find_route(self, pathname: str) -> Optional[Dict[str, Any]]:
        """
        查找匹配的路由
        
        Args:
            pathname: 路径名
            
        Returns:
            Optional[Dict]: 路由配置
        """
        # 精确匹配
        if pathname in self.routes:
            return self.routes[pathname]
        
        # 模式匹配（简单实现）
        for route_path, route_config in self.routes.items():
            if self._match_route_pattern(pathname, route_path):
                return route_config
        
        return None
    
    def _match_route_pattern(self, pathname: str, pattern: str) -> bool:
        """
        匹配路由模式
        
        Args:
            pathname: 实际路径
            pattern: 路由模式
            
        Returns:
            bool: 是否匹配
        """
        # 简单的通配符匹配
        if '*' in pattern:
            prefix = pattern.split('*')[0]
            return pathname.startswith(prefix)
        
        return pathname == pattern
    
    def _check_permissions(self, required_permissions: List[str], 
                          user_session: dict) -> bool:
        """
        检查权限
        
        Args:
            required_permissions: 所需权限列表
            user_session: 用户会话数据
            
        Returns:
            bool: 是否有权限
        """
        if not required_permissions:
            return True
        
        if not user_session or not user_session.get('user_id'):
            return False
        
        user_permissions = user_session.get('permissions', [])
        
        # 检查是否拥有所有必需权限
        for permission in required_permissions:
            if permission not in user_permissions:
                return False
        
        return True
    
    def _handle_error(self, error_code: int, message: str = None):
        """
        处理错误
        
        Args:
            error_code: 错误代码
            message: 错误消息
            
        Returns:
            tuple: (错误页面内容, 错误标题)
        """
        # 使用自定义错误处理器
        if error_code in self.error_handlers:
            try:
                return self.error_handlers[error_code](message)
            except Exception as e:
                logger.error(f"错误处理器异常: {e}")
        
        # 默认错误处理
        error_messages = {
            404: "页面不存在",
            403: "权限不足",
            500: "服务器内部错误"
        }
        
        default_message = error_messages.get(error_code, "未知错误")
        display_message = message or default_message
        
        error_content = html.Div([
            html.Div([
                html.H1(f"错误 {error_code}", className="error-title"),
                html.P(display_message, className="error-message"),
                html.A("返回首页", href="/", className="error-link")
            ], className="error-content")
        ], className="error-container")
        
        error_title = f"错误 {error_code} - 现代化后台管理系统"
        
        return error_content, error_title


def create_route_manager(app) -> RouteManager:
    """
    创建路由管理器
    
    Args:
        app: Dash应用实例
        
    Returns:
        RouteManager: 路由管理器实例
    """
    return RouteManager(app)


# 路由装饰器
def route(path: str, title: str = None, permissions: List[str] = None):
    """
    路由装饰器
    
    Args:
        path: 路由路径
        title: 页面标题
        permissions: 所需权限列表
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        func._route_path = path
        func._route_title = title
        func._route_permissions = permissions or []
        return func
    return decorator


# 中间件装饰器
def middleware(func):
    """
    中间件装饰器
    
    Args:
        func: 中间件函数
        
    Returns:
        装饰器函数
    """
    func._is_middleware = True
    return func


# 权限检查中间件
@middleware
def auth_middleware(request_context: dict):
    """
    认证中间件
    
    Args:
        request_context: 请求上下文
        
    Returns:
        None或重定向内容
    """
    pathname = request_context['pathname']
    user_session = request_context['user_session']
    
    # 公开页面不需要认证
    public_paths = ['/', '/login', '/register', '/health', '/api/version']
    
    if pathname in public_paths or pathname.startswith('/assets/'):
        return None
    
    # 检查用户是否已登录
    if not user_session or not user_session.get('user_id'):
        # 如果已经在登录页面，不需要重定向
        if pathname == '/login':
            return None
            # 重定向到登录页面
        return html.Div([
            dcc.Location(pathname='/login', id='redirect-login')
        ]), "请登录"
    
    # 用户已登录，继续处理
    
    return None


# 日志中间件
@middleware
def logging_middleware(request_context: dict):
    """
    日志中间件
    
    Args:
        request_context: 请求上下文
        
    Returns:
        None
    """
    pathname = request_context['pathname']
    user_session = request_context['user_session']
    
    # 记录访问日志
    user_id = user_session.get('user_id', 'anonymous') if user_session else 'anonymous'
    logger.info(f"页面访问: {pathname} - 用户: {user_id}")
    
    return None