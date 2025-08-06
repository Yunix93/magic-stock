"""
权限装饰器模块

提供高级权限控制装饰器
"""

from functools import wraps
from typing import Callable, Union, List, Optional, Dict, Any
from flask import request, jsonify, g
from app.core.auth import get_current_user
from app.core.permissions import permission_checker, has_permission, has_role
from app.core.exceptions import AuthenticationError, AuthorizationError
import logging

logger = logging.getLogger(__name__)


def require_permissions(*permission_names: str, operator: str = 'AND'):
    """
    多权限验证装饰器
    
    Args:
        *permission_names: 权限名称列表
        operator: 逻辑操作符，'AND' 或 'OR'
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
            
            # 检查权限
            if operator.upper() == 'AND':
                # 需要拥有所有权限
                missing_permissions = [
                    perm for perm in permission_names 
                    if not has_permission(user, perm)
                ]
                if missing_permissions:
                    error_msg = f'缺少必需权限: {", ".join(missing_permissions)}'
                    if request.is_json or request.path.startswith('/api/'):
                        return jsonify({
                            'success': False,
                            'error': 'PermissionDenied',
                            'message': error_msg,
                            'missing_permissions': missing_permissions,
                            'code': 403
                        }), 403
                    else:
                        raise AuthorizationError(error_msg)
            else:  # OR
                # 只需要拥有其中一个权限
                has_any_permission = any(
                    has_permission(user, perm) for perm in permission_names
                )
                if not has_any_permission:
                    error_msg = f'需要以下权限之一: {", ".join(permission_names)}'
                    if request.is_json or request.path.startswith('/api/'):
                        return jsonify({
                            'success': False,
                            'error': 'PermissionDenied',
                            'message': error_msg,
                            'required_permissions': list(permission_names),
                            'code': 403
                        }), 403
                    else:
                        raise AuthorizationError(error_msg)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_roles(*role_names: str, operator: str = 'OR'):
    """
    多角色验证装饰器
    
    Args:
        *role_names: 角色名称列表
        operator: 逻辑操作符，'AND' 或 'OR'
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
            
            # 检查角色
            if operator.upper() == 'AND':
                # 需要拥有所有角色
                missing_roles = [
                    role for role in role_names 
                    if not has_role(user, role)
                ]
                if missing_roles:
                    error_msg = f'缺少必需角色: {", ".join(missing_roles)}'
                    if request.is_json or request.path.startswith('/api/'):
                        return jsonify({
                            'success': False,
                            'error': 'PermissionDenied',
                            'message': error_msg,
                            'missing_roles': missing_roles,
                            'code': 403
                        }), 403
                    else:
                        raise AuthorizationError(error_msg)
            else:  # OR
                # 只需要拥有其中一个角色
                has_any_role = any(
                    has_role(user, role) for role in role_names
                )
                if not has_any_role:
                    error_msg = f'需要以下角色之一: {", ".join(role_names)}'
                    if request.is_json or request.path.startswith('/api/'):
                        return jsonify({
                            'success': False,
                            'error': 'PermissionDenied',
                            'message': error_msg,
                            'required_roles': list(role_names),
                            'code': 403
                        }), 403
                    else:
                        raise AuthorizationError(error_msg)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def resource_owner_or_permission(resource_param: str, permission_name: str, 
                                user_id_field: str = 'user_id'):
    """
    资源所有者或权限验证装饰器
    
    允许资源所有者或具有特定权限的用户访问
    
    Args:
        resource_param: 资源参数名称（从URL参数或请求体获取）
        permission_name: 备用权限名称
        user_id_field: 资源中用户ID字段名称
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
            
            # 获取资源ID
            resource_id = None
            if resource_param in kwargs:
                resource_id = kwargs[resource_param]
            elif resource_param in request.args:
                resource_id = request.args.get(resource_param)
            elif request.is_json:
                data = request.get_json() or {}
                resource_id = data.get(resource_param)
            
            # 检查是否为资源所有者
            is_owner = False
            if resource_id:
                # 这里需要根据实际业务逻辑来检查所有权
                # 示例：检查用户是否为资源所有者
                if resource_param == 'user_id' and str(resource_id) == str(user.id):
                    is_owner = True
                # 可以添加更多资源类型的所有权检查逻辑
            
            # 如果不是所有者，检查是否有权限
            if not is_owner and not has_permission(user, permission_name):
                error_msg = f'您只能访问自己的资源或需要权限: {permission_name}'
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'PermissionDenied',
                        'message': error_msg,
                        'code': 403
                    }), 403
                else:
                    raise AuthorizationError(error_msg)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def conditional_permission(condition_func: Callable, permission_name: str):
    """
    条件权限验证装饰器
    
    根据条件函数的结果决定是否需要权限验证
    
    Args:
        condition_func: 条件函数，接收用户和请求参数，返回布尔值
        permission_name: 需要的权限名称
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
            
            # 检查条件
            try:
                needs_permission = condition_func(user, request, *args, **kwargs)
            except Exception as e:
                logger.error(f"条件函数执行失败: {e}")
                needs_permission = True  # 默认需要权限
            
            # 如果需要权限，进行权限检查
            if needs_permission and not has_permission(user, permission_name):
                error_msg = f'当前操作需要权限: {permission_name}'
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'PermissionDenied',
                        'message': error_msg,
                        'required_permission': permission_name,
                        'code': 403
                    }), 403
                else:
                    raise AuthorizationError(error_msg)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit_by_role(limits: Dict[str, int], window: int = 3600):
    """
    基于角色的限流装饰器
    
    Args:
        limits: 角色限制映射，如 {'admin': 1000, 'user': 100}
        window: 时间窗口（秒）
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
            
            # 获取用户角色对应的限制
            user_limit = None
            from app.services.user_service import user_service
            try:
                roles = user_service.get_user_roles(user.id)
                for role in roles:
                    if role.name in limits:
                        role_limit = limits[role.name]
                        if user_limit is None or role_limit > user_limit:
                            user_limit = role_limit
            except Exception as e:
                logger.warning(f"获取用户角色限制失败: {e}")
            
            # 如果没有找到对应的限制，使用默认限制
            if user_limit is None:
                user_limit = limits.get('default', 10)
            
            # 这里应该实现实际的限流逻辑
            # 可以使用Redis或内存缓存来跟踪请求次数
            # 示例实现（需要实际的限流逻辑）
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def audit_log(action: str, resource: str = None, 
              get_resource_id: Callable = None):
    """
    审计日志装饰器
    
    自动记录用户操作日志
    
    Args:
        action: 操作类型
        resource: 资源类型
        get_resource_id: 获取资源ID的函数
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            # 执行原函数
            try:
                result = f(*args, **kwargs)
                
                # 记录成功的操作日志
                if user:
                    resource_id = None
                    if get_resource_id:
                        try:
                            resource_id = get_resource_id(*args, **kwargs)
                        except Exception as e:
                            logger.warning(f"获取资源ID失败: {e}")
                    
                    # 创建操作日志
                    try:
                        from app.services.log_service import log_service
                        log_service.create_operation_log(
                            user_id=user.id,
                            operation=action,
                            resource=resource or f.__name__,
                            details={
                                'function': f.__name__,
                                'resource_id': resource_id,
                                'ip_address': request.remote_addr,
                                'user_agent': request.headers.get('User-Agent'),
                                'success': True
                            },
                            ip_address=request.remote_addr
                        )
                    except Exception as e:
                        logger.error(f"记录操作日志失败: {e}")
                
                return result
                
            except Exception as e:
                # 记录失败的操作日志
                if user:
                    try:
                        from app.services.log_service import log_service
                        log_service.create_operation_log(
                            user_id=user.id,
                            operation=action,
                            resource=resource or f.__name__,
                            details={
                                'function': f.__name__,
                                'error': str(e),
                                'ip_address': request.remote_addr,
                                'user_agent': request.headers.get('User-Agent'),
                                'success': False
                            },
                            ip_address=request.remote_addr
                        )
                    except Exception as log_error:
                        logger.error(f"记录操作日志失败: {log_error}")
                
                raise
        return decorated_function
    return decorator


# 便捷的权限装饰器组合
def user_management_required(f: Callable) -> Callable:
    """用户管理权限装饰器"""
    return require_permissions('user:list', 'user:read')(f)


def role_management_required(f: Callable) -> Callable:
    """角色管理权限装饰器"""
    return require_permissions('role:list', 'role:read')(f)


def system_admin_required(f: Callable) -> Callable:
    """系统管理员权限装饰器"""
    return require_roles('admin')(f)


def manager_or_admin_required(f: Callable) -> Callable:
    """管理员或经理权限装饰器"""
    return require_roles('admin', 'manager')(f)