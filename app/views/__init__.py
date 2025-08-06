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
        permissions=[]  # 暂时移除权限要求
    )
    
    # 注册用户管理路由
    app.route_manager.register_route(
        path='/users',
        layout_func=create_users_layout,
        title='用户管理 - 现代化后台管理系统',
        permissions=[]  # 暂时移除权限要求
    )
    
    # 注册系统设置路由
    app.route_manager.register_route(
        path='/system',
        layout_func=create_system_layout,
        title='系统设置 - 现代化后台管理系统',
        permissions=[]  # 暂时移除权限要求
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

__all__ = ['register_layouts', 'layout_manager', 'login_layout']