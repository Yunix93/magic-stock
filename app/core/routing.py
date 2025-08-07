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
                      middleware: List[Callable] = None, lazy: bool = False,
                      cache_timeout: int = 300):
        """
        注册路由
        
        Args:
            path: 路由路径
            layout_func: 布局函数
            title: 页面标题
            permissions: 所需权限列表
            middleware: 中间件列表
            lazy: 是否懒加载
            cache_timeout: 缓存超时时间（秒）
        """
        self.routes[path] = {
            'layout_func': layout_func,
            'title': title or '现代化后台管理系统',
            'permissions': permissions or [],
            'middleware': middleware or [],
            'lazy': lazy,
            'cache_timeout': cache_timeout,
            'cache': {}  # 页面缓存
        }
        
        logger.info(f"注册路由: {path} (懒加载: {lazy})")
    
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
        route_result = self._find_route_with_params(pathname)
        
        if not route_result:
            return self._handle_error(404, f"页面不存在: {pathname}")
        
        route_config, route_params = route_result
        
        # 将路由参数添加到请求上下文
        request_context['route_params'] = route_params
        
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
            # 检查是否启用懒加载和缓存
            if route_config.get('lazy', False):
                cached_content = self._get_cached_content(pathname, route_config, request_context)
                if cached_content:
                    return cached_content, route_config['title']
            
            layout_func = route_config['layout_func']
            
            # 如果是懒加载，显示加载指示器
            if route_config.get('lazy', False):
                page_content = self._create_lazy_loading_content(layout_func, request_context)
            else:
                page_content = layout_func(request_context)
            
            page_title = route_config['title']
            
            # 缓存页面内容
            if route_config.get('lazy', False):
                self._cache_content(pathname, route_config, page_content, request_context)
            
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
    
    def _find_route_with_params(self, pathname: str) -> Optional[tuple]:
        """
        查找匹配的路由并提取参数
        
        Args:
            pathname: 路径名
            
        Returns:
            Optional[tuple]: (路由配置, 路由参数)
        """
        # 精确匹配
        if pathname in self.routes:
            return self.routes[pathname], {}
        
        # 模式匹配并提取参数
        for route_path, route_config in self.routes.items():
            if self._match_route_pattern(pathname, route_path):
                route_params = self.extract_route_params(pathname, route_path)
                return route_config, route_params
        
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
        # 支持参数路由，如 /users/<int:user_id>
        if '<' in pattern and '>' in pattern:
            return self._match_parameterized_route(pathname, pattern)
        
        # 简单的通配符匹配
        if '*' in pattern:
            prefix = pattern.split('*')[0]
            return pathname.startswith(prefix)
        
        return pathname == pattern
    
    def _match_parameterized_route(self, pathname: str, pattern: str) -> bool:
        """
        匹配参数化路由 - 使用简单的分段匹配方式
        
        Args:
            pathname: 实际路径
            pattern: 路由模式，如 /users/<int:user_id>
            
        Returns:
            bool: 是否匹配
        """
        # 将路径和模式都按 '/' 分割
        path_parts = [p for p in pathname.split('/') if p]
        pattern_parts = [p for p in pattern.split('/') if p]
        
        # 如果段数不匹配，直接返回False
        if len(path_parts) != len(pattern_parts):
            return False
        
        # 逐段匹配
        for path_part, pattern_part in zip(path_parts, pattern_parts):
            if not self._match_route_segment(path_part, pattern_part):
                return False
        
        return True
    
    def _match_route_segment(self, path_segment: str, pattern_segment: str) -> bool:
        """
        匹配单个路由段
        
        Args:
            path_segment: 路径段，如 "123"
            pattern_segment: 模式段，如 "<int:user_id>" 或 "users"
            
        Returns:
            bool: 是否匹配
        """
        # 如果是精确匹配
        if not pattern_segment.startswith('<') or not pattern_segment.endswith('>'):
            return path_segment == pattern_segment
        
        # 解析参数类型
        param_content = pattern_segment[1:-1]  # 去掉 < >
        
        if ':' in param_content:
            param_type, param_name = param_content.split(':', 1)
        else:
            param_type = 'str'
            param_name = param_content
        
        # 根据参数类型验证
        if param_type == 'int':
            return path_segment.isdigit()
        elif param_type == 'str':
            return len(path_segment) > 0 and '/' not in path_segment
        else:
            # 默认按字符串处理
            return len(path_segment) > 0 and '/' not in path_segment
    
    def extract_route_params(self, pathname: str, pattern: str) -> Dict[str, Any]:
        """
        提取路由参数 - 使用简单的分段提取方式
        
        Args:
            pathname: 实际路径
            pattern: 路由模式
            
        Returns:
            Dict[str, Any]: 路由参数
        """
        if '<' not in pattern or '>' not in pattern:
            return {}
        
        # 将路径和模式都按 '/' 分割
        path_parts = [p for p in pathname.split('/') if p]
        pattern_parts = [p for p in pattern.split('/') if p]
        
        # 如果段数不匹配，返回空字典
        if len(path_parts) != len(pattern_parts):
            return {}
        
        params = {}
        
        # 逐段提取参数
        for path_part, pattern_part in zip(path_parts, pattern_parts):
            if pattern_part.startswith('<') and pattern_part.endswith('>'):
                # 解析参数
                param_content = pattern_part[1:-1]  # 去掉 < >
                
                if ':' in param_content:
                    param_type, param_name = param_content.split(':', 1)
                else:
                    param_type = 'str'
                    param_name = param_content
                
                # 根据类型转换值
                if param_type == 'int':
                    if path_part.isdigit():
                        params[param_name] = int(path_part)
                    else:
                        # 类型不匹配，返回空字典
                        return {}
                else:
                    params[param_name] = path_part
        
        return params
    
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
    
    def _get_cached_content(self, pathname: str, route_config: dict, request_context: dict):
        """
        获取缓存的页面内容
        
        Args:
            pathname: 路径名
            route_config: 路由配置
            request_context: 请求上下文
            
        Returns:
            缓存的页面内容或None
        """
        import time
        
        cache = route_config.get('cache', {})
        cache_key = self._generate_cache_key(pathname, request_context)
        
        if cache_key in cache:
            cached_item = cache[cache_key]
            cache_time = cached_item.get('timestamp', 0)
            cache_timeout = route_config.get('cache_timeout', 300)
            
            # 检查缓存是否过期
            if time.time() - cache_time < cache_timeout:
                logger.debug(f"使用缓存内容: {pathname}")
                return cached_item.get('content')
            else:
                # 清除过期缓存
                del cache[cache_key]
        
        return None
    
    def _cache_content(self, pathname: str, route_config: dict, content, request_context: dict):
        """
        缓存页面内容
        
        Args:
            pathname: 路径名
            route_config: 路由配置
            content: 页面内容
            request_context: 请求上下文
        """
        import time
        
        cache = route_config.get('cache', {})
        cache_key = self._generate_cache_key(pathname, request_context)
        
        cache[cache_key] = {
            'content': content,
            'timestamp': time.time()
        }
        
        # 限制缓存大小，防止内存泄漏
        if len(cache) > 100:
            # 删除最旧的缓存项
            oldest_key = min(cache.keys(), key=lambda k: cache[k]['timestamp'])
            del cache[oldest_key]
        
        logger.debug(f"缓存页面内容: {pathname}")
    
    def _generate_cache_key(self, pathname: str, request_context: dict) -> str:
        """
        生成缓存键
        
        Args:
            pathname: 路径名
            request_context: 请求上下文
            
        Returns:
            str: 缓存键
        """
        import hashlib
        
        # 基于路径、查询参数和用户ID生成缓存键
        user_id = request_context.get('user_session', {}).get('user_id', 'anonymous')
        query_str = request_context.get('search', '')
        
        cache_data = f"{pathname}:{query_str}:{user_id}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _create_lazy_loading_content(self, layout_func: Callable, request_context: dict):
        """
        创建懒加载内容
        
        Args:
            layout_func: 布局函数
            request_context: 请求上下文
            
        Returns:
            懒加载页面内容
        """
        # 创建加载指示器
        loading_content = html.Div([
            html.Div([
                html.Div(className="loading-spinner"),
                html.P("页面加载中...", className="loading-text")
            ], className="loading-container"),
            
            # 使用dcc.Interval来异步加载实际内容
            dcc.Interval(
                id=f'lazy-load-{request_context["pathname"].replace("/", "-")}',
                interval=100,  # 100ms后加载
                n_intervals=0,
                max_intervals=1
            )
        ], className="lazy-loading-wrapper")
        
        return loading_content
    
    def clear_cache(self, pathname: str = None):
        """
        清除缓存
        
        Args:
            pathname: 要清除的路径，None表示清除所有缓存
        """
        if pathname:
            # 清除特定路径的缓存
            for route_path, route_config in self.routes.items():
                if route_path == pathname:
                    route_config['cache'] = {}
                    logger.info(f"清除路由缓存: {pathname}")
                    break
        else:
            # 清除所有缓存
            for route_config in self.routes.values():
                route_config['cache'] = {}
            logger.info("清除所有路由缓存")
    
    def get_route_stats(self) -> Dict[str, Any]:
        """
        获取路由统计信息
        
        Returns:
            Dict[str, Any]: 路由统计信息
        """
        stats = {
            'total_routes': len(self.routes),
            'cached_routes': 0,
            'cache_size': 0,
            'routes': {}
        }
        
        for path, config in self.routes.items():
            cache = config.get('cache', {})
            cache_size = len(cache)
            
            if cache_size > 0:
                stats['cached_routes'] += 1
                stats['cache_size'] += cache_size
            
            stats['routes'][path] = {
                'title': config.get('title'),
                'permissions': config.get('permissions', []),
                'lazy': config.get('lazy', False),
                'cache_size': cache_size
            }
        
        return stats


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