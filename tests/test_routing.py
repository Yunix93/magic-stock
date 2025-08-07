"""
路由系统集成测试

测试路由管理器的各种功能
"""

import pytest
import time
from unittest.mock import Mock, patch
from dash import html, dcc

from app.core.routing import RouteManager, create_route_manager, route, middleware


class TestRouteManager:
    """路由管理器测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.mock_app = Mock()
        self.route_manager = RouteManager(self.mock_app)
    
    def test_route_registration(self):
        """测试路由注册"""
        def test_layout(request_context):
            return html.Div("Test Page")
        
        # 注册路由
        self.route_manager.register_route(
            path='/test',
            layout_func=test_layout,
            title='测试页面',
            permissions=['test.view']
        )
        
        # 验证路由已注册
        assert '/test' in self.route_manager.routes
        route_config = self.route_manager.routes['/test']
        assert route_config['title'] == '测试页面'
        assert route_config['permissions'] == ['test.view']
        assert route_config['layout_func'] == test_layout
    
    def test_middleware_registration(self):
        """测试中间件注册"""
        def test_middleware(request_context):
            return None
        
        # 注册中间件
        self.route_manager.register_middleware(test_middleware)
        
        # 验证中间件已注册
        assert test_middleware in self.route_manager.middleware
    
    def test_error_handler_registration(self):
        """测试错误处理器注册"""
        def test_error_handler(message):
            return html.Div(f"Error: {message}"), "Error"
        
        # 注册错误处理器
        self.route_manager.register_error_handler(404, test_error_handler)
        
        # 验证错误处理器已注册
        assert 404 in self.route_manager.error_handlers
        assert self.route_manager.error_handlers[404] == test_error_handler
    
    def test_route_pattern_matching(self):
        """测试路由模式匹配"""
        # 测试精确匹配
        assert self.route_manager._match_route_pattern('/test', '/test') == True
        assert self.route_manager._match_route_pattern('/test', '/other') == False
        
        # 测试通配符匹配
        assert self.route_manager._match_route_pattern('/api/users', '/api/*') == True
        assert self.route_manager._match_route_pattern('/other/users', '/api/*') == False
        
        # 测试参数化路由匹配
        assert self.route_manager._match_route_pattern('/users/123', '/users/<int:user_id>') == True
        assert self.route_manager._match_route_pattern('/users/abc', '/users/<int:user_id>') == False
        assert self.route_manager._match_route_pattern('/users/abc', '/users/<str:username>') == True
    
    def test_route_parameter_extraction(self):
        """测试路由参数提取"""
        # 测试整数参数
        params = self.route_manager.extract_route_params('/users/123', '/users/<int:user_id>')
        assert params == {'user_id': 123}
        
        # 测试字符串参数
        params = self.route_manager.extract_route_params('/users/john', '/users/<str:username>')
        assert params == {'username': 'john'}
        
        # 测试多个参数
        params = self.route_manager.extract_route_params(
            '/users/123/posts/456', 
            '/users/<int:user_id>/posts/<int:post_id>'
        )
        assert params == {'user_id': 123, 'post_id': 456}
        
        # 测试无参数路由
        params = self.route_manager.extract_route_params('/users', '/users')
        assert params == {}
    
    def test_permission_checking(self):
        """测试权限检查"""
        # 测试无权限要求
        assert self.route_manager._check_permissions([], {}) == True
        
        # 测试未登录用户
        assert self.route_manager._check_permissions(['test.view'], {}) == False
        assert self.route_manager._check_permissions(['test.view'], {'user_id': None}) == False
        
        # 测试已登录用户有权限
        user_session = {
            'user_id': 1,
            'permissions': ['test.view', 'test.edit']
        }
        assert self.route_manager._check_permissions(['test.view'], user_session) == True
        assert self.route_manager._check_permissions(['test.view', 'test.edit'], user_session) == True
        
        # 测试已登录用户无权限
        assert self.route_manager._check_permissions(['admin.manage'], user_session) == False
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        request_context = {
            'pathname': '/test',
            'search': '',
            'user_session': {'user_id': 1}
        }
        
        route_config = {
            'cache': {},
            'cache_timeout': 300
        }
        
        # 测试缓存键生成
        cache_key = self.route_manager._generate_cache_key('/test', request_context)
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length
        
        # 测试缓存存储
        test_content = html.Div("Cached Content")
        self.route_manager._cache_content('/test', route_config, test_content, request_context)
        
        # 验证内容已缓存
        assert len(route_config['cache']) == 1
        
        # 测试缓存获取
        cached_content = self.route_manager._get_cached_content('/test', route_config, request_context)
        assert cached_content == test_content
    
    def test_cache_expiration(self):
        """测试缓存过期"""
        request_context = {
            'pathname': '/test',
            'search': '',
            'user_session': {'user_id': 1}
        }
        
        route_config = {
            'cache': {},
            'cache_timeout': 1  # 1秒过期
        }
        
        # 缓存内容
        test_content = html.Div("Cached Content")
        self.route_manager._cache_content('/test', route_config, test_content, request_context)
        
        # 立即获取应该有缓存
        cached_content = self.route_manager._get_cached_content('/test', route_config, request_context)
        assert cached_content == test_content
        
        # 等待缓存过期
        time.sleep(1.1)
        
        # 过期后应该没有缓存
        cached_content = self.route_manager._get_cached_content('/test', route_config, request_context)
        assert cached_content is None
    
    def test_route_stats(self):
        """测试路由统计"""
        # 注册几个路由
        def layout1(ctx): return html.Div("Page 1")
        def layout2(ctx): return html.Div("Page 2")
        
        self.route_manager.register_route('/page1', layout1, lazy=True)
        self.route_manager.register_route('/page2', layout2, permissions=['admin'])
        
        # 添加一些缓存
        self.route_manager.routes['/page1']['cache']['key1'] = {'content': 'cached', 'timestamp': time.time()}
        
        # 获取统计信息
        stats = self.route_manager.get_route_stats()
        
        assert stats['total_routes'] == 2
        assert stats['cached_routes'] == 1
        assert stats['cache_size'] == 1
        assert '/page1' in stats['routes']
        assert '/page2' in stats['routes']
        assert stats['routes']['/page1']['lazy'] == True
        assert stats['routes']['/page2']['permissions'] == ['admin']
    
    def test_cache_clearing(self):
        """测试缓存清除"""
        # 设置一些缓存
        self.route_manager.routes['/test1'] = {'cache': {'key1': 'value1'}}
        self.route_manager.routes['/test2'] = {'cache': {'key2': 'value2'}}
        
        # 清除特定路由缓存
        self.route_manager.clear_cache('/test1')
        assert self.route_manager.routes['/test1']['cache'] == {}
        assert self.route_manager.routes['/test2']['cache'] == {'key2': 'value2'}
        
        # 清除所有缓存
        self.route_manager.clear_cache()
        assert self.route_manager.routes['/test2']['cache'] == {}


class TestRouteDecorators:
    """路由装饰器测试"""
    
    def test_route_decorator(self):
        """测试路由装饰器"""
        @route('/decorated', title='装饰器路由', permissions=['test.view'])
        def decorated_layout(request_context):
            return html.Div("Decorated Route")
        
        # 验证装饰器属性
        assert hasattr(decorated_layout, '_route_path')
        assert decorated_layout._route_path == '/decorated'
        assert decorated_layout._route_title == '装饰器路由'
        assert decorated_layout._route_permissions == ['test.view']
    
    def test_middleware_decorator(self):
        """测试中间件装饰器"""
        @middleware
        def decorated_middleware(request_context):
            return None
        
        # 验证装饰器属性
        assert hasattr(decorated_middleware, '_is_middleware')
        assert decorated_middleware._is_middleware == True


class TestRouteIntegration:
    """路由系统集成测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.mock_app = Mock()
        self.route_manager = create_route_manager(self.mock_app)
    
    def test_full_route_handling(self):
        """测试完整的路由处理流程"""
        # 注册测试路由
        def test_layout(request_context):
            user_id = request_context.get('route_params', {}).get('user_id', 'unknown')
            return html.Div(f"User ID: {user_id}")
        
        self.route_manager.register_route(
            path='/users/<int:user_id>',
            layout_func=test_layout,
            title='用户详情',
            permissions=['user.view']
        )
        
        # 模拟用户会话
        user_session = {
            'user_id': 1,
            'permissions': ['user.view']
        }
        
        # 测试路由处理
        content, title = self.route_manager._handle_route('/users/123', '', user_session)
        
        # 验证结果
        assert title == '用户详情'
        # 注意：由于我们模拟了layout函数，实际的内容验证需要根据具体实现调整
    
    def test_middleware_execution_order(self):
        """测试中间件执行顺序"""
        execution_order = []
        
        def middleware1(request_context):
            execution_order.append('middleware1')
            return None
        
        def middleware2(request_context):
            execution_order.append('middleware2')
            return None
        
        # 注册中间件
        self.route_manager.register_middleware(middleware1)
        self.route_manager.register_middleware(middleware2)
        
        # 注册测试路由
        def test_layout(request_context):
            execution_order.append('layout')
            return html.Div("Test")
        
        self.route_manager.register_route('/test', test_layout)
        
        # 执行路由处理
        self.route_manager._handle_route('/test', '', {'user_id': 1})
        
        # 验证执行顺序
        assert execution_order == ['middleware1', 'middleware2', 'layout']
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试404错误
        content, title = self.route_manager._handle_route('/nonexistent', '', {})
        assert '404' in title
        
        # 测试403权限错误
        def protected_layout(request_context):
            return html.Div("Protected")
        
        self.route_manager.register_route(
            '/protected', 
            protected_layout, 
            permissions=['admin.access']
        )
        
        # 无权限用户访问
        content, title = self.route_manager._handle_route('/protected', '', {'user_id': 1, 'permissions': []})
        assert '403' in title
        
        # 未登录用户访问
        content, title = self.route_manager._handle_route('/protected', '', {})
        assert '403' in title


if __name__ == '__main__':
    pytest.main([__file__])