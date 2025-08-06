"""
布局组件

提供应用的主要布局组件，包括导航栏、侧边栏、内容区域等
"""

from dash import html, dcc
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LayoutManager:
    """布局管理器"""
    
    def __init__(self):
        """初始化布局管理器"""
        self.current_user = None
        self.user_permissions = []
        
    def create_main_layout(self, content: html.Div = None, 
                          user_session: Dict[str, Any] = None) -> html.Div:
        """
        创建主布局
        
        Args:
            content: 页面内容
            user_session: 用户会话数据
            
        Returns:
            html.Div: 主布局组件
        """
        # 直接使用user_session作为用户数据，因为认证回调中用户信息直接存储在session中
        self.current_user = user_session if user_session and user_session.get('user_id') else None
        self.user_permissions = user_session.get('permissions', []) if user_session else []
        
        # 调试信息
        if user_session:
            logger.info(f"布局组件接收到用户会话: user_id={user_session.get('user_id')}, username={user_session.get('username')}")
            logger.info(f"用户权限: {self.user_permissions}")
        else:
            logger.info("布局组件未接收到用户会话数据")
        
        return html.Div([
            # 顶部导航栏
            self._create_header(),
            
            # 主要内容区域
            html.Div([
                # 侧边导航菜单
                self._create_sidebar(),
                
                # 内容区域
                html.Div([
                    # 面包屑导航
                    self._create_breadcrumb(),
                    
                    # 页面内容
                    html.Div(
                        content or self._create_default_content(),
                        id='main-content',
                        className='main-content'
                    )
                ], className='content-wrapper')
                
            ], className='main-wrapper'),
            
            # 页脚
            self._create_footer()
            
        ], className='app-layout')
    
    def _create_header(self) -> html.Header:
        """创建顶部导航栏"""
        return html.Header([
            html.Div([
                # Logo和标题
                html.Div([
                    html.Img(
                        src='/assets/imgs/logo.svg',
                        className='logo-img',
                        style={'display': 'none'}  # 如果没有logo图片就隐藏
                    ),
                    html.H1('现代化后台管理系统', className='app-title')
                ], className='header-brand'),
                
                # 导航菜单
                html.Nav([
                    html.Ul([
                        html.Li([
                            html.A('首页', href='/', className='nav-link')
                        ], className='nav-item'),
                        
                        html.Li([
                            html.A('用户管理', href='/users', className='nav-link')
                        ], className='nav-item') if self._has_permission('user.view') else None,
                        
                        html.Li([
                            html.A('系统设置', href='/system', className='nav-link')
                        ], className='nav-item') if self._has_permission('system.manage') else None,
                        
                    ], className='nav-menu')
                ], className='header-nav'),
                
                # 用户信息和操作
                html.Div([
                    self._create_user_dropdown() if self.current_user else html.A(
                        '登录', 
                        href='/login', 
                        className='login-btn'
                    )
                ], className='header-actions')
                
            ], className='header-container')
        ], className='app-header')
    
    def _create_sidebar(self) -> html.Aside:
        """创建侧边导航菜单"""
        if not self.current_user:
            return html.Aside(className='sidebar sidebar-hidden')
        
        menu_items = self._get_menu_items()
        
        return html.Aside([
            html.Div([
                # 用户信息简要显示
                html.Div([
                    html.Div([
                        html.Img(
                            src='/assets/imgs/default-avatar.svg',  # 使用默认头像
                            className='user-avatar-small'
                        ),
                        html.Div([
                            html.Div(self.current_user.get('full_name') or self.current_user.get('username', '用户'), className='user-name'),
                            html.Div('超级管理员' if self.current_user.get('is_superuser') else '普通用户', className='user-role')
                        ], className='user-info')
                    ], className='sidebar-user')
                ], className='sidebar-header'),
                
                # 导航菜单
                html.Nav([
                    html.Ul([
                        self._create_menu_item(item) for item in menu_items
                    ], className='sidebar-menu')
                ], className='sidebar-nav')
                
            ], className='sidebar-content')
        ], className='sidebar')
    
    def _create_user_dropdown(self) -> html.Div:
        """创建用户下拉菜单"""
        return html.Div([
            html.Button([
                html.Img(
                    src='/assets/imgs/default-avatar.svg',  # 使用默认头像
                    className='user-avatar'
                ),
                html.Span(self.current_user.get('full_name') or self.current_user.get('username', '用户'), className='user-name'),
                html.I(className='dropdown-arrow')
            ], className='user-dropdown-btn', id='user-dropdown-btn'),
            
            html.Div([
                html.A([
                    html.I(className='icon-user'),
                    html.Span('个人资料')
                ], href='/profile', className='dropdown-item'),
                
                html.A([
                    html.I(className='icon-settings'),
                    html.Span('账户设置')
                ], href='/settings', className='dropdown-item'),
                
                html.Hr(className='dropdown-divider'),
                
                html.A([
                    html.I(className='icon-logout'),
                    html.Span('退出登录')
                ], href='/logout', className='dropdown-item logout-item')
                
            ], className='user-dropdown-menu', id='user-dropdown-menu')
            
        ], className='user-dropdown')
    
    def _create_breadcrumb(self) -> html.Nav:
        """创建面包屑导航"""
        return html.Nav([
            html.Ol([
                html.Li([
                    html.A('首页', href='/')
                ], className='breadcrumb-item'),
                
                html.Li([
                    html.Span('当前页面', id='current-page-breadcrumb')
                ], className='breadcrumb-item active')
                
            ], className='breadcrumb')
        ], className='breadcrumb-nav', id='breadcrumb-nav')
    
    def _create_footer(self) -> html.Footer:
        """创建页脚"""
        return html.Footer([
            html.Div([
                html.P([
                    '© 2024 现代化后台管理系统. ',
                    html.A('使用条款', href='/terms', className='footer-link'),
                    ' | ',
                    html.A('隐私政策', href='/privacy', className='footer-link')
                ], className='footer-text'),
                
                html.P([
                    '版本 1.0.0 | ',
                    html.A('技术支持', href='/support', className='footer-link')
                ], className='footer-info')
                
            ], className='footer-container')
        ], className='app-footer')
    
    def _create_default_content(self) -> html.Div:
        """创建默认内容"""
        return html.Div([
            html.Div([
                html.H2('欢迎使用现代化后台管理系统', className='welcome-title'),
                html.P('这是一个功能完整的企业级后台管理系统', className='welcome-description'),
                
                html.Div([
                    html.Div([
                        html.I(className='feature-icon icon-users'),
                        html.H3('用户管理'),
                        html.P('完整的用户管理功能，支持用户创建、编辑、权限分配等操作')
                    ], className='feature-card'),
                    
                    html.Div([
                        html.I(className='feature-icon icon-shield'),
                        html.H3('权限控制'),
                        html.P('基于角色的权限控制系统，灵活的权限分配和管理')
                    ], className='feature-card'),
                    
                    html.Div([
                        html.I(className='feature-icon icon-chart'),
                        html.H3('数据统计'),
                        html.P('实时的数据统计和分析，帮助您更好地了解系统运行状况')
                    ], className='feature-card'),
                    
                    html.Div([
                        html.I(className='feature-icon icon-settings'),
                        html.H3('系统设置'),
                        html.P('灵活的系统配置选项，满足不同场景的使用需求')
                    ], className='feature-card')
                    
                ], className='features-grid')
                
            ], className='welcome-content')
        ], className='default-content')
    
    def _get_menu_items(self) -> List[Dict[str, Any]]:
        """获取菜单项"""
        menu_items = [
            {
                'title': '仪表板',
                'icon': 'icon-dashboard',
                'href': '/dashboard',
                'permission': None
            },
            {
                'title': '用户管理',
                'icon': 'icon-users',
                'href': '/users',
                'permission': 'user.view',
                'children': [
                    {
                        'title': '用户列表',
                        'href': '/users/list',
                        'permission': 'user.view'
                    },
                    {
                        'title': '添加用户',
                        'href': '/users/add',
                        'permission': 'user.create'
                    }
                ]
            },
            {
                'title': '角色权限',
                'icon': 'icon-shield',
                'href': '/roles',
                'permission': 'role.view',
                'children': [
                    {
                        'title': '角色管理',
                        'href': '/roles/list',
                        'permission': 'role.view'
                    },
                    {
                        'title': '权限管理',
                        'href': '/permissions',
                        'permission': 'permission.view'
                    }
                ]
            },
            {
                'title': '系统监控',
                'icon': 'icon-monitor',
                'href': '/monitor',
                'permission': 'system.monitor',
                'children': [
                    {
                        'title': '系统状态',
                        'href': '/monitor/status',
                        'permission': 'system.monitor'
                    },
                    {
                        'title': '操作日志',
                        'href': '/monitor/logs',
                        'permission': 'log.view'
                    }
                ]
            },
            {
                'title': '系统设置',
                'icon': 'icon-settings',
                'href': '/system',
                'permission': 'system.manage',
                'children': [
                    {
                        'title': '基础设置',
                        'href': '/system/basic',
                        'permission': 'system.manage'
                    },
                    {
                        'title': '安全设置',
                        'href': '/system/security',
                        'permission': 'system.security'
                    }
                ]
            }
        ]
        
        # 过滤用户没有权限的菜单项
        return [item for item in menu_items if self._has_permission(item.get('permission'))]
    
    def _create_menu_item(self, item: Dict[str, Any]) -> html.Li:
        """创建菜单项"""
        children = item.get('children', [])
        has_children = len(children) > 0
        
        if has_children:
            # 有子菜单的项
            return html.Li([
                html.A([
                    html.I(className=item['icon']),
                    html.Span(item['title']),
                    html.I(className='submenu-arrow')
                ], className='menu-link has-submenu', **{'data-href': item['href']}),
                
                html.Ul([
                    html.Li([
                        html.A(child['title'], href=child['href'], className='submenu-link')
                    ], className='submenu-item')
                    for child in children if self._has_permission(child.get('permission'))
                ], className='submenu')
                
            ], className='menu-item has-submenu')
        else:
            # 普通菜单项
            return html.Li([
                html.A([
                    html.I(className=item['icon']),
                    html.Span(item['title'])
                ], href=item['href'], className='menu-link')
            ], className='menu-item')
    
    def _has_permission(self, permission: Optional[str]) -> bool:
        """检查用户是否有指定权限"""
        if not permission:
            return True
        
        if not self.current_user:
            return False
        
        # 超级用户拥有所有权限
        if self.current_user.get('is_superuser'):
            return True
        
        return permission in self.user_permissions


class LoginLayout:
    """登录页面布局"""
    
    @staticmethod
    def create_login_layout() -> html.Div:
        """创建登录页面布局"""
        return html.Div([
            html.Div([
                # 登录表单容器
                html.Div([
                    # Logo和标题
                    html.Div([
                        html.Img(
                            src='/assets/imgs/logo.svg',
                            className='login-logo',
                            style={'display': 'none'}  # 如果没有logo就隐藏
                        ),
                        html.H1('现代化后台管理系统', className='login-title'),
                        html.P('请登录您的账户', className='login-subtitle')
                    ], className='login-header'),
                    
                    # 登录表单
                    html.Div([
                        # 用户名输入
                        html.Div([
                            html.Label('用户名或邮箱', className='form-label'),
                            html.Div([
                                html.I(className='input-icon icon-user'),
                                dcc.Input(
                                    id='login-username',
                                    type='text',
                                    placeholder='请输入用户名或邮箱',
                                    className='form-input',
                                    required=True
                                )
                            ], className='input-group')
                        ], className='form-group'),
                        
                        # 密码输入
                        html.Div([
                            html.Label('密码', className='form-label'),
                            html.Div([
                                html.I(className='input-icon icon-lock'),
                                dcc.Input(
                                    id='login-password',
                                    type='password',
                                    placeholder='请输入密码',
                                    className='form-input',
                                    required=True
                                )
                            ], className='input-group')
                        ], className='form-group'),
                        
                        # 记住我和忘记密码
                        html.Div([
                            html.Label([
                                dcc.Checklist(
                                    id='remember-me',
                                    options=[{'label': '记住我', 'value': 'remember'}],
                                    value=[],
                                    className='checkbox'
                                )
                            ], className='checkbox-label'),
                            
                            html.A('忘记密码？', href='/forgot-password', className='forgot-link')
                        ], className='form-options'),
                        
                        # 登录按钮
                        html.Button(
                            '登录',
                            id='login-submit',
                            n_clicks=0,
                            className='login-button'
                        ),
                        
                        # 错误消息显示
                        html.Div(id='login-error', className='error-message'),
                        
                        # 成功消息显示
                        html.Div(id='login-success', className='success-message')
                        
                    ], className='login-form', id='login-form'),
                    
                    # 其他选项
                    html.Div([
                        html.P([
                            '还没有账户？',
                            html.A('立即注册', href='/register', className='register-link')
                        ], className='register-prompt'),
                        

                    ], className='login-footer')
                    
                ], className='login-card'),
                
                # 背景装饰
                html.Div(className='login-background')
                
            ], className='login-container')
        ], className='login-layout')


# 全局布局管理器实例
layout_manager = LayoutManager()
login_layout = LoginLayout()