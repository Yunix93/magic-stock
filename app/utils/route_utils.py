"""
路由工具函数

提供路由相关的工具函数和管理功能
"""

import logging
from typing import Dict, List, Any, Optional
from dash import html, dcc, dash_table
import pandas as pd

logger = logging.getLogger(__name__)


class RouteAnalyzer:
    """路由分析器"""
    
    def __init__(self, route_manager):
        """
        初始化路由分析器
        
        Args:
            route_manager: 路由管理器实例
        """
        self.route_manager = route_manager
    
    def analyze_routes(self) -> Dict[str, Any]:
        """
        分析路由配置
        
        Returns:
            Dict[str, Any]: 路由分析结果
        """
        routes = self.route_manager.routes
        
        analysis = {
            'total_routes': len(routes),
            'protected_routes': 0,
            'lazy_routes': 0,
            'cached_routes': 0,
            'permission_coverage': {},
            'cache_efficiency': {},
            'route_details': []
        }
        
        for path, config in routes.items():
            # 统计受保护的路由
            permissions = config.get('permissions', [])
            if permissions:
                analysis['protected_routes'] += 1
                
                # 统计权限覆盖
                for perm in permissions:
                    if perm not in analysis['permission_coverage']:
                        analysis['permission_coverage'][perm] = 0
                    analysis['permission_coverage'][perm] += 1
            
            # 统计懒加载路由
            if config.get('lazy', False):
                analysis['lazy_routes'] += 1
            
            # 统计缓存路由
            cache = config.get('cache', {})
            if cache:
                analysis['cached_routes'] += 1
                analysis['cache_efficiency'][path] = len(cache)
            
            # 收集路由详情
            analysis['route_details'].append({
                'path': path,
                'title': config.get('title', ''),
                'permissions': permissions,
                'lazy': config.get('lazy', False),
                'cache_timeout': config.get('cache_timeout', 0),
                'cache_size': len(cache)
            })
        
        return analysis
    
    def generate_route_report(self) -> html.Div:
        """
        生成路由报告页面
        
        Returns:
            html.Div: 路由报告页面内容
        """
        analysis = self.analyze_routes()
        
        # 创建统计卡片
        stats_cards = html.Div([
            html.Div([
                html.H3(str(analysis['total_routes'])),
                html.P('总路由数')
            ], className='stat-card'),
            
            html.Div([
                html.H3(str(analysis['protected_routes'])),
                html.P('受保护路由')
            ], className='stat-card'),
            
            html.Div([
                html.H3(str(analysis['lazy_routes'])),
                html.P('懒加载路由')
            ], className='stat-card'),
            
            html.Div([
                html.H3(str(analysis['cached_routes'])),
                html.P('缓存路由')
            ], className='stat-card')
        ], className='stats-grid')
        
        # 创建路由详情表格
        if analysis['route_details']:
            df = pd.DataFrame(analysis['route_details'])
            
            route_table = dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[
                    {'name': '路径', 'id': 'path'},
                    {'name': '标题', 'id': 'title'},
                    {'name': '权限', 'id': 'permissions'},
                    {'name': '懒加载', 'id': 'lazy', 'type': 'text'},
                    {'name': '缓存超时', 'id': 'cache_timeout', 'type': 'numeric'},
                    {'name': '缓存大小', 'id': 'cache_size', 'type': 'numeric'}
                ],
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{lazy} = True'},
                        'backgroundColor': '#e6f7ff',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{cache_size} > 0'},
                        'backgroundColor': '#f6ffed',
                        'color': 'black',
                    }
                ],
                sort_action='native',
                filter_action='native',
                page_action='native',
                page_current=0,
                page_size=10
            )
        else:
            route_table = html.P('暂无路由数据')
        
        # 权限覆盖图表
        permission_chart = self._create_permission_chart(analysis['permission_coverage'])
        
        return html.Div([
            html.H1('路由系统报告', className='page-title'),
            
            html.Div([
                html.H2('路由统计'),
                stats_cards
            ], className='section'),
            
            html.Div([
                html.H2('权限覆盖'),
                permission_chart
            ], className='section'),
            
            html.Div([
                html.H2('路由详情'),
                route_table
            ], className='section')
        ])
    
    def _create_permission_chart(self, permission_coverage: Dict[str, int]) -> html.Div:
        """
        创建权限覆盖图表
        
        Args:
            permission_coverage: 权限覆盖数据
            
        Returns:
            html.Div: 权限图表
        """
        if not permission_coverage:
            return html.P('暂无权限数据')
        
        # 创建简单的条形图
        max_count = max(permission_coverage.values())
        
        bars = []
        for perm, count in sorted(permission_coverage.items()):
            width_percent = (count / max_count) * 100
            bars.append(
                html.Div([
                    html.Div([
                        html.Span(perm, className='bar-label'),
                        html.Span(str(count), className='bar-value')
                    ], className='bar-info'),
                    html.Div([
                        html.Div(
                            style={'width': f'{width_percent}%'},
                            className='bar-fill'
                        )
                    ], className='bar-container')
                ], className='permission-bar')
            )
        
        return html.Div(bars, className='permission-chart')


class RoutePerformanceMonitor:
    """路由性能监控器"""
    
    def __init__(self, route_manager):
        """
        初始化性能监控器
        
        Args:
            route_manager: 路由管理器实例
        """
        self.route_manager = route_manager
        self.access_log = []
        self.performance_data = {}
    
    def log_route_access(self, path: str, user_id: str, load_time: float):
        """
        记录路由访问
        
        Args:
            path: 路由路径
            user_id: 用户ID
            load_time: 加载时间（秒）
        """
        import time
        
        self.access_log.append({
            'path': path,
            'user_id': user_id,
            'load_time': load_time,
            'timestamp': time.time()
        })
        
        # 限制日志大小
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-500:]
        
        # 更新性能数据
        if path not in self.performance_data:
            self.performance_data[path] = {
                'total_accesses': 0,
                'total_load_time': 0,
                'min_load_time': float('inf'),
                'max_load_time': 0
            }
        
        perf = self.performance_data[path]
        perf['total_accesses'] += 1
        perf['total_load_time'] += load_time
        perf['min_load_time'] = min(perf['min_load_time'], load_time)
        perf['max_load_time'] = max(perf['max_load_time'], load_time)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计
        
        Returns:
            Dict[str, Any]: 性能统计数据
        """
        stats = {}
        
        for path, data in self.performance_data.items():
            if data['total_accesses'] > 0:
                avg_load_time = data['total_load_time'] / data['total_accesses']
                stats[path] = {
                    'total_accesses': data['total_accesses'],
                    'avg_load_time': round(avg_load_time, 3),
                    'min_load_time': round(data['min_load_time'], 3),
                    'max_load_time': round(data['max_load_time'], 3)
                }
        
        return stats
    
    def get_slow_routes(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """
        获取慢路由列表
        
        Args:
            threshold: 慢路由阈值（秒）
            
        Returns:
            List[Dict[str, Any]]: 慢路由列表
        """
        slow_routes = []
        stats = self.get_performance_stats()
        
        for path, data in stats.items():
            if data['avg_load_time'] > threshold:
                slow_routes.append({
                    'path': path,
                    'avg_load_time': data['avg_load_time'],
                    'total_accesses': data['total_accesses']
                })
        
        # 按平均加载时间排序
        slow_routes.sort(key=lambda x: x['avg_load_time'], reverse=True)
        return slow_routes


def create_route_management_page(route_manager) -> html.Div:
    """
    创建路由管理页面
    
    Args:
        route_manager: 路由管理器实例
        
    Returns:
        html.Div: 路由管理页面
    """
    analyzer = RouteAnalyzer(route_manager)
    
    # 获取路由统计
    stats = route_manager.get_route_stats()
    
    return html.Div([
        html.H1('路由管理', className='page-title'),
        
        # 操作按钮
        html.Div([
            html.Button('清除所有缓存', id='clear-all-cache-btn', className='btn btn-warning'),
            html.Button('刷新统计', id='refresh-stats-btn', className='btn btn-primary'),
            html.Button('导出报告', id='export-report-btn', className='btn btn-success')
        ], className='btn-group'),
        
        # 统计信息
        html.Div([
            html.H2('路由统计'),
            html.Div([
                html.Div([
                    html.H3(str(stats['total_routes'])),
                    html.P('总路由数')
                ], className='stat-card'),
                
                html.Div([
                    html.H3(str(stats['cached_routes'])),
                    html.P('缓存路由数')
                ], className='stat-card'),
                
                html.Div([
                    html.H3(str(stats['cache_size'])),
                    html.P('总缓存项数')
                ], className='stat-card')
            ], className='stats-grid')
        ], className='section'),
        
        # 路由详情
        html.Div([
            html.H2('路由详情'),
            html.Div(id='route-details-container')
        ], className='section'),
        
        # 性能监控
        html.Div([
            html.H2('性能监控'),
            html.Div(id='performance-monitor-container')
        ], className='section')
    ])


# 全局路由工具实例
route_analyzer = None
performance_monitor = None


def init_route_tools(route_manager):
    """
    初始化路由工具
    
    Args:
        route_manager: 路由管理器实例
    """
    global route_analyzer, performance_monitor
    
    route_analyzer = RouteAnalyzer(route_manager)
    performance_monitor = RoutePerformanceMonitor(route_manager)
    
    logger.info("路由工具初始化完成")


def get_route_analyzer():
    """获取路由分析器"""
    return route_analyzer


def get_performance_monitor():
    """获取性能监控器"""
    return performance_monitor