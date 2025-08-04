"""
认证装饰器模块

提供登录验证和权限验证装饰器
"""

from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user
from flask_principal import Permission, RoleNeed, identity_loaded
import logging

logger = logging.getLogger(__name__)


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录以访问此页面', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_name):
    """权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录以访问此页面', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            # 检查用户权限
            permission = Permission(RoleNeed(permission_name))
            if not permission.can():
                flash('您没有权限访问此页面', 'error')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """管理员权限验证装饰器"""
    return permission_required('admin')(f)


def check_user_permission(user, permission_name):
    """检查用户是否具有指定权限"""
    if not user or not user.is_authenticated:
        return False
    
    # 管理员拥有所有权限
    if hasattr(user, 'is_admin') and user.is_admin:
        return True
    
    # 检查用户角色权限
    if hasattr(user, 'roles'):
        for role in user.roles:
            if role.name == permission_name:
                return True
            
            # 检查角色的具体权限
            if hasattr(role, 'permissions'):
                for perm in role.permissions:
                    if perm.name == permission_name:
                        return True
    
    return False