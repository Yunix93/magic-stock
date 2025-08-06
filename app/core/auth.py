"""
认证装饰器模块

提供现代化的登录验证和权限验证装饰器
"""

from functools import wraps
from typing import Optional, Union, List, Callable, Any
from flask import request, jsonify, g
import jwt
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.config_manager import config_manager
# 延迟导入避免循环依赖
# from app.services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)


def extract_token_from_request() -> Optional[str]:
    """从请求中提取JWT令牌"""
    # 从Authorization头提取
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]  # 移除 'Bearer ' 前缀
    
    # 从查询参数提取
    token = request.args.get('token')
    if token:
        return token
    
    # 从表单数据提取
    token = request.form.get('token')
    if token:
        return token
    
    return None


def get_current_user():
    """获取当前用户"""
    if hasattr(g, 'current_user'):
        return g.current_user
    
    token = extract_token_from_request()
    if not token:
        return None
    
    try:
        # 延迟导入并验证令牌获取用户
        import importlib
        auth_service_module = importlib.import_module('app.services.auth_service')
        auth_service = auth_service_module.auth_service
        user = auth_service.get_current_user(token)
        g.current_user = user
        return user
    except Exception as e:
        logger.warning(f"获取当前用户失败: {e}")
        return None


def login_required(f: Callable) -> Callable:
    """
    登录验证装饰器
    
    用于需要用户登录才能访问的接口
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'AuthenticationRequired',
                    'message': '请先登录以访问此资源',
                    'code': 401
                }), 401
            else:
                # 对于Web页面，可以重定向到登录页面
                raise AuthenticationError("请先登录以访问此页面")
        
        # 将用户信息传递给视图函数
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_name: str, resource: Optional[str] = None):
    """
    权限验证装饰器
    
    Args:
        permission_name: 权限名称，格式为 'resource:action' 或直接权限名
        resource: 资源名称（可选，如果permission_name已包含则忽略）
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'AuthenticationRequired',
                        'message': '请先登录以访问此资源',
                        'code': 401
                    }), 401
                else:
                    raise AuthenticationError("请先登录以访问此页面")
            
            # 检查用户权限
            from app.services.user_service import user_service
            has_permission = user_service.check_user_permission(user.id, permission_name)
            if not has_permission:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'PermissionDenied',
                        'message': f'您没有权限执行此操作: {permission_name}',
                        'code': 403
                    }), 403
                else:
                    raise AuthorizationError(f"您没有权限访问此页面: {permission_name}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(role_names: Union[str, List[str]]):
    """
    角色验证装饰器
    
    Args:
        role_names: 角色名称或角色名称列表
    """
    if isinstance(role_names, str):
        role_names = [role_names]
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'AuthenticationRequired',
                        'message': '请先登录以访问此资源',
                        'code': 401
                    }), 401
                else:
                    raise AuthenticationError("请先登录以访问此页面")
            
            # 检查用户角色
            from app.services.user_service import user_service
            has_role = any(user_service.check_user_role(user.id, role_name) for role_name in role_names)
            if not has_role:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'PermissionDenied',
                        'message': f'您没有所需的角色权限: {", ".join(role_names)}',
                        'code': 403
                    }), 403
                else:
                    raise AuthorizationError(f"您没有所需的角色权限: {', '.join(role_names)}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f: Callable) -> Callable:
    """
    管理员权限验证装饰器
    
    要求用户具有管理员角色或超级用户权限
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'AuthenticationRequired',
                    'message': '请先登录以访问此资源',
                    'code': 401
                }), 401
            else:
                raise AuthenticationError("请先登录以访问此页面")
        
        # 检查管理员权限
        from app.services.user_service import user_service
        is_admin = user_service.is_user_admin(user.id)
        
        if not is_admin:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'PermissionDenied',
                    'message': '需要管理员权限才能访问此资源',
                    'code': 403
                }), 403
            else:
                raise AuthorizationError("需要管理员权限才能访问此页面")
        
        return f(*args, **kwargs)
    return decorated_function


def superuser_required(f: Callable) -> Callable:
    """
    超级用户权限验证装饰器
    
    要求用户具有超级用户权限
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'AuthenticationRequired',
                    'message': '请先登录以访问此资源',
                    'code': 401
                }), 401
            else:
                raise AuthenticationError("请先登录以访问此页面")
        
        # 检查超级用户权限
        if not getattr(user, 'is_superuser', False):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'PermissionDenied',
                    'message': '需要超级用户权限才能访问此资源',
                    'code': 403
                }), 403
            else:
                raise AuthorizationError("需要超级用户权限才能访问此页面")
        
        return f(*args, **kwargs)
    return decorated_function


def check_user_permission(user, permission_name: str) -> bool:
    """
    检查用户是否具有指定权限
    
    Args:
        user: 用户对象
        permission_name: 权限名称
        
    Returns:
        bool: 是否具有权限
    """
    if not user:
        return False
    
    # 超级用户拥有所有权限
    if getattr(user, 'is_superuser', False):
        return True
    
    # 使用用户服务的权限检查方法
    from app.services.user_service import user_service
    return user_service.check_user_permission(user.id, permission_name)


def check_user_role(user, role_name: str) -> bool:
    """
    检查用户是否具有指定角色
    
    Args:
        user: 用户对象
        role_name: 角色名称
        
    Returns:
        bool: 是否具有角色
    """
    if not user:
        return False
    
    # 使用用户服务的角色检查方法
    from app.services.user_service import user_service
    return user_service.check_user_role(user.id, role_name)


def optional_auth(f: Callable) -> Callable:
    """
    可选认证装饰器
    
    如果用户已登录则设置用户信息，但不强制要求登录
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        # 无论是否有用户都继续执行
        return f(*args, **kwargs)
    return decorated_function