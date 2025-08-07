"""
视图模块

包含所有页面布局和组件
"""

from .components.layout import layout_manager, login_layout

def register_layouts(app):
    """注册所有页面布局"""
    from app.core.routing import route
    
    # 注册主页面布局路由
    app.route_manager.register_route(
        path='/dashboard',
        layout_func=create_dashboard_layout,
        title='仪表板 - 现代化后台管理系统',
        permissions=['dashboard.view'],
        lazy=False,  # 仪表板不使用懒加载，需要快速显示
        cache_timeout=60  # 缓存1分钟
    )
    
    # 注册用户管理路由
    app.route_manager.register_route(
        path='/users',
        layout_func=create_users_layout,
        title='用户管理 - 现代化后台管理系统',
        permissions=['user.view'],
        lazy=True,  # 用户管理页面使用懒加载
        cache_timeout=300  # 缓存5分钟
    )
    
    # 注册用户详情路由（支持参数）
    app.route_manager.register_route(
        path='/users/<int:user_id>',
        layout_func=create_user_detail_layout,
        title='用户详情 - 现代化后台管理系统',
        permissions=['user.view'],
        lazy=True,
        cache_timeout=180  # 缓存3分钟
    )
    
    # 注册系统设置路由
    app.route_manager.register_route(
        path='/system',
        layout_func=create_system_layout,
        title='系统设置 - 现代化后台管理系统',
        permissions=['system.manage'],
        lazy=True,
        cache_timeout=600  # 缓存10分钟
    )
    
    # 注册系统监控路由
    app.route_manager.register_route(
        path='/monitor',
        layout_func=create_monitor_layout,
        title='系统监控 - 现代化后台管理系统',
        permissions=['system.monitor'],
        lazy=True,
        cache_timeout=30  # 监控数据缓存30秒
    )
    
    print("✅ 页面布局注册完成")

def create_dashboard_layout(request_context):
    """创建仪表板布局"""
    from dash import html
    
    content = html.Div([
        html.H1('仪表板', className='page-title'),
        html.Div([
            html.Div([
                html.H3('系统概览'),
                html.P('这里显示系统的基本统计信息')
            ], className='card'),
            
            html.Div([
                html.H3('最近活动'),
                html.P('这里显示最近的用户活动')
            ], className='card'),
            
            html.Div([
                html.H3('快速操作'),
                html.Div([
                    html.A('添加用户', href='/users/add', className='btn btn-primary'),
                    html.A('系统设置', href='/system', className='btn btn-secondary')
                ], className='btn-group')
            ], className='card')
        ], className='dashboard-grid')
    ])
    
    return layout_manager.create_main_layout(
        content=content,
        user_session=request_context.get('user_session')
    )

def create_users_layout(request_context):
    """创建用户管理布局"""
    from dash import html, dcc, dash_table
    
    content = html.Div([
        html.H1('用户管理', className='page-title'),
        
        html.Div([
            html.Div([
                html.H3('用户列表'),
                html.Div([
                    dcc.Input(
                        id='user-search',
                        type='text',
                        placeholder='搜索用户...',
                        className='form-input'
                    ),
                    html.Button('搜索', className='btn btn-primary'),
                    html.Button('添加用户', className='btn btn-success')
                ], className='search-bar'),
                
                html.Div(id='users-table-container', children=[
                    html.P('用户列表将在这里显示')
                ])
            ], className='card')
        ])
    ])
    
    return layout_manager.create_main_layout(
        content=content,
        user_session=request_context.get('user_session')
    )

def create_system_layout(request_context):
    """创建系统设置布局"""
    from dash import html, dcc
    
    content = html.Div([
        html.H1('系统设置', className='page-title'),
        
        html.Div([
            html.Div([
                html.H3('基础设置'),
                html.Div([
                    html.Div([
                        html.Label('系统名称', className='form-label'),
                        dcc.Input(
                            id='system-name',
                            type='text',
                            value='现代化后台管理系统',
                            className='form-input'
                        )
                    ], className='form-group'),
                    
                    html.Div([
                        html.Label('系统描述', className='form-label'),
                        dcc.Textarea(
                            id='system-description',
                            value='企业级后台管理系统',
                            className='form-textarea'
                        )
                    ], className='form-group'),
                    
                    html.Button('保存设置', className='btn btn-primary')
                ], className='form')
            ], className='card'),
            
            html.Div([
                html.H3('安全设置'),
                html.Div([
                    html.Div([
                        html.Label('密码最小长度', className='form-label'),
                        dcc.Input(
                            id='password-min-length',
                            type='number',
                            value=8,
                            className='form-input'
                        )
                    ], className='form-group'),
                    
                    html.Div([
                        html.Label('登录失败锁定次数', className='form-label'),
                        dcc.Input(
                            id='max-login-attempts',
                            type='number',
                            value=5,
                            className='form-input'
                        )
                    ], className='form-group'),
                    
                    html.Button('保存安全设置', className='btn btn-primary')
                ], className='form')
            ], className='card')
        ])
    ])
    
    return layout_manager.create_main_layout(
        content=content,
        user_session=request_context.get('user_session')
    )

def create_user_detail_layout(request_context):
    """创建用户详情布局"""
    from dash import html, dcc
    
    # 获取路由参数
    user_id = request_context.get('route_params', {}).get('user_id', 0)
    
    content = html.Div([
        html.H1(f'用户详情 (ID: {user_id})', className='page-title'),
        
        html.Div([
            html.Div([
                html.H3('基本信息'),
                html.Div([
                    html.Div([
                        html.Label('用户ID', className='form-label'),
                        html.P(str(user_id), className='form-value')
                    ], className='form-group'),
                    
                    html.Div([
                        html.Label('用户名', className='form-label'),
                        html.P(f'user_{user_id}', className='form-value')
                    ], className='form-group'),
                    
                    html.Div([
                        html.Label('邮箱', className='form-label'),
                        html.P(f'user_{user_id}@example.com', className='form-value')
                    ], className='form-group'),
                    
                    html.Div([
                        html.A('编辑用户', href=f'/users/{user_id}/edit', className='btn btn-primary'),
                        html.A('返回列表', href='/users', className='btn btn-secondary')
                    ], className='btn-group')
                ])
            ], className='card')
        ])
    ])
    
    return layout_manager.create_main_layout(
        content=content,
        user_session=request_context.get('user_session')
    )

def create_monitor_layout(request_context):
    """创建系统监控布局"""
    from dash import html, dcc
    import time
    
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    
    content = html.Div([
        html.H1('系统监控', className='page-title'),
        
        html.Div([
            html.Div([
                html.H3('系统状态'),
                html.Div([
                    html.Div([
                        html.H4('CPU使用率'),
                        html.Div([
                            html.Div(className='progress-bar', style={'width': '45%'}),
                        ], className='progress'),
                        html.P('45%', className='progress-text')
                    ], className='monitor-item'),
                    
                    html.Div([
                        html.H4('内存使用率'),
                        html.Div([
                            html.Div(className='progress-bar', style={'width': '62%'}),
                        ], className='progress'),
                        html.P('62%', className='progress-text')
                    ], className='monitor-item'),
                    
                    html.Div([
                        html.H4('磁盘使用率'),
                        html.Div([
                            html.Div(className='progress-bar', style={'width': '38%'}),
                        ], className='progress'),
                        html.P('38%', className='progress-text')
                    ], className='monitor-item')
                ])
            ], className='card'),
            
            html.Div([
                html.H3('实时信息'),
                html.Div([
                    html.P(f'当前时间: {current_time}'),
                    html.P('在线用户: 12'),
                    html.P('活跃会话: 8'),
                    html.P('系统运行时间: 15天 3小时 42分钟')
                ])
            ], className='card')
        ], className='dashboard-grid')
    ])
    
    return layout_manager.create_main_layout(
        content=content,
        user_session=request_context.get('user_session')
    )

__all__ = ['register_layouts', 'layout_manager', 'login_layout']