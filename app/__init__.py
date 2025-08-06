"""
现代化后台管理系统

基于 Dash + Flask 的企业级后台管理系统
支持用户认证、权限管理、数据管理等功能
"""

__version__ = "1.0.0"
__author__ = "Admin System Team"

import os
import sys
from flask import Flask, request, jsonify
from dash import Dash, html, dcc
from dash.exceptions import PreventUpdate
import logging
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    应用工厂函数
    
    Args:
        config_name: 配置环境名称 ('development', 'production', 'testing')
        
    Returns:
        tuple: (dash_app, flask_server)
    """
    from app.config import config
    from app.core.extensions import init_extensions
    from app.core.config_manager import config_manager
    
    # 自动检测配置环境
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    logger.info(f"开始创建应用，环境: {config_name}")
    
    # 创建 Flask 应用
    server = Flask(__name__)
    
    # 加载配置
    config_class = config.get(config_name, config['default'])
    server.config.from_object(config_class)
    
    # 从配置管理器获取各种配置
    jwt_config = config_manager.get_jwt_config()
    security_config = config_manager.get_security_config()
    
    # 更新Flask配置
    server.config.update(jwt_config)
    server.config.update(security_config)
    
    # 设置应用标题
    app_title = server.config.get('APP_TITLE', '现代化后台管理系统')
    
    # 初始化配置
    config_class.init_app(server)
    
    # 创建 Dash 应用
    app = Dash(
        __name__,
        server=server,
        title=app_title,
        suppress_callback_exceptions=True,
        compress=True,
        update_title=None,
        assets_folder='../assets',  # 指定assets文件夹路径
        external_stylesheets=[
            # Ant Design CSS
            'https://cdn.jsdelivr.net/npm/antd@5.0.0/dist/reset.css'
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"},
            {"name": "description", "content": "现代化后台管理系统"},
            {"name": "author", "content": "Admin System Team"}
        ]
    )
    
    # 配置应用基础参数
    _configure_app_settings(app, server, config_name)
    
    # 初始化扩展
    init_extensions(app, server)
    
    # 设置全局异常处理
    _setup_error_handlers(app, server)
    
    # 设置中间件
    _setup_middleware(server)
    
    # 设置应用路由和URL管理
    _setup_routing(app, server)
    
    # 注册蓝图和回调
    _register_components(app, server)
    
    # 设置应用布局
    _setup_app_layout(app)
    
    logger.info(f"应用创建成功，配置: {config_name}")
    logger.info(f"应用标题: {app_title}")
    
    return app, server


def _configure_app_settings(app, server, config_name):
    """配置应用基础参数"""
    
    # 开发环境特殊配置
    if config_name == 'development':
        app.enable_dev_tools(
            debug=True,
            dev_tools_hot_reload=True,
            dev_tools_ui=True,
            dev_tools_serve_dev_bundles=True,
            dev_tools_hot_reload_interval=1000,
            dev_tools_hot_reload_watch_interval=500
        )
        logger.info("🔧 开发工具已启用")
    
    # 生产环境配置
    elif config_name == 'production':
        app.enable_dev_tools(
            debug=False,
            dev_tools_hot_reload=False,
            dev_tools_ui=False
        )
        logger.info("🏭 生产环境配置已应用")
    
    # 注意：compress和suppress_callback_exceptions只能在构造函数中设置
    # 这些配置已经在create_app中的Dash构造函数中设置了
    
    logger.info("⚙️ 应用基础参数配置完成")


def _setup_error_handlers(app, server):
    """设置全局异常处理机制"""
    
    @server.errorhandler(404)
    def not_found_error(error):
        """404错误处理"""
        logger.warning(f"404错误: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': '请求的资源不存在',
                'error_code': 'NOT_FOUND'
            }), 404
        
        # 对于Dash页面，返回到主页面
        return app.index(), 404
    
    @server.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        logger.error(f"500错误: {error}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }), 500
        
        # 对于Dash页面，显示错误页面
        return html.Div([
            html.H1("系统错误", className="error-title"),
            html.P("系统遇到了一个错误，请稍后重试。", className="error-message"),
            html.A("返回首页", href="/", className="error-link")
        ], className="error-container"), 500
    
    @server.errorhandler(403)
    def forbidden_error(error):
        """403权限错误处理"""
        logger.warning(f"403权限错误: {request.url}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': '权限不足',
                'error_code': 'FORBIDDEN'
            }), 403
        
        return html.Div([
            html.H1("权限不足", className="error-title"),
            html.P("您没有权限访问此页面。", className="error-message"),
            html.A("返回首页", href="/", className="error-link")
        ], className="error-container"), 403
    
    # Dash回调异常处理将在具体的回调函数中处理
    # 这里不需要全局的回调异常处理器
    
    logger.info("全局异常处理机制设置完成")


def _setup_middleware(server):
    """设置中间件"""
    
    @server.before_request
    def before_request():
        """请求前处理"""
        # 记录请求信息
        if not request.path.startswith('/assets/'):
            logger.debug(f"请求: {request.method} {request.path}")
        
        # 安全头设置
        if request.path.startswith('/api/'):
            # API请求的安全检查
            pass
    
    @server.after_request
    def after_request(response):
        """请求后处理"""
        # 设置安全头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CORS设置（如果需要）
        if server.config.get('ENABLE_CORS', False):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    logger.info("中间件设置完成")


def _setup_routing(app, server):
    """设置应用路由和URL管理"""
    from app.core.routing import create_route_manager, auth_middleware, logging_middleware
    
    # 创建路由管理器
    route_manager = create_route_manager(app)
    
    # 注册全局中间件
    route_manager.register_middleware(logging_middleware)
    route_manager.register_middleware(auth_middleware)
    
    # 注册默认路由
    route_manager.register_route(
        path='/',
        layout_func=_create_home_layout,
        title='首页 - 现代化后台管理系统'
    )
    
    # 注册登录路由
    route_manager.register_route(
        path='/login',
        layout_func=_create_login_layout,
        title='用户登录 - 现代化后台管理系统'
    )
    
    # 存储路由管理器到应用中
    app.route_manager = route_manager
    
    # Flask路由
    # 健康检查端点
    @server.route('/health')
    def health_check():
        """健康检查端点"""
        import time
        return jsonify({
            'status': 'healthy',
            'version': __version__,
            'timestamp': time.time(),
            'uptime': time.time() - server.config.get('START_TIME', time.time())
        })
    
    # API版本信息端点
    @server.route('/api/version')
    def api_version():
        """API版本信息"""
        return jsonify({
            'version': __version__,
            'api_version': 'v1',
            'author': __author__,
            'description': '现代化后台管理系统API'
        })
    
    # 静态文件路由（如果需要自定义处理）
    @server.route('/assets/<path:filename>')
    def serve_assets(filename):
        """静态资源服务"""
        from flask import send_from_directory
        import os
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        logger.debug(f"静态文件请求: {filename}, 路径: {assets_dir}")
        return send_from_directory(assets_dir, filename)
    
    # 记录启动时间
    import time
    server.config['START_TIME'] = time.time()
    
    logger.info("应用路由设置完成")


def _register_components(app, server):
    """注册蓝图和回调"""
    
    try:
        # 注册API蓝图
        from app.api import register_api_blueprints
        register_api_blueprints(server)
        logger.info("API蓝图注册完成")
    except ImportError as e:
        logger.warning(f"API蓝图注册失败: {e}")
    
    try:
        # 注册页面布局
        from app.views import register_layouts
        register_layouts(app)
        logger.info("页面布局注册完成")
    except ImportError as e:
        logger.warning(f"页面布局注册失败: {e}")
    
    try:
        # 注册回调函数
        from app.callbacks import register_callbacks
        register_callbacks(app)
        logger.info("回调函数注册完成")
    except ImportError as e:
        logger.warning(f"回调函数注册失败: {e}")


def _setup_app_layout(app):
    """设置应用布局"""
    
    # 设置基础布局
    app.layout = html.Div([
        # 页面标题
        dcc.Store(id='page-title', data='现代化后台管理系统'),
        
        # 用户会话存储
        dcc.Store(id='user-session', storage_type='session'),
        
        # 全局状态存储
        dcc.Store(id='global-state', storage_type='memory'),
        
        # URL路由组件
        dcc.Location(id='url', refresh=False),
        
        # 主要内容区域
        html.Div(id='page-content', children=[
            # 默认加载页面
            html.Div([
                html.H1("现代化后台管理系统", className="welcome-title"),
                html.P("系统正在加载中...", className="welcome-message"),
                html.Div(className="loading-spinner")
            ], className="welcome-container")
        ])
    ], id='app-container')
    
    logger.info("应用布局设置完成")


def _create_home_layout(request_context):
    """创建首页布局"""
    return html.Div([
        html.Div([
            html.H1("欢迎使用现代化后台管理系统", className="welcome-title"),
            html.P("这是一个基于Dash的企业级后台管理系统", className="welcome-message"),
            html.Div([
                html.A("用户管理", href="/users", className="nav-button"),
                html.A("系统设置", href="/system", className="nav-button"),
                html.A("登录", href="/login", className="nav-button")
            ], className="nav-buttons")
        ], className="welcome-container")
    ])


def _create_login_layout(request_context):
    """创建登录页面布局"""
    from app.views.components.layout import login_layout
    return login_layout.create_login_layout()


# 导出主要函数和变量
__all__ = ['create_app', '__version__', '__author__']