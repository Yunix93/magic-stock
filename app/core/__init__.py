"""
核心功能模块

包含认证、权限、异常处理等核心功能
"""

from .auth import login_required, permission_required
from .permissions import Permission, RolePermission
from .exceptions import (
    BaseAppException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    BusinessLogicError
)
from .utils import generate_uuid, hash_password, verify_password
from .constants import (
    UserStatus,
    UserRole,
    LogLevel,
    CacheKeys,
    APIMessages,
    ConfigDefaults,
    HTTPStatus,
    DateFormats
)
from .decorators import (
    log_execution_time,
    handle_exceptions,
    validate_json,
    cache_result,
    retry
)
from .validators import (
    validate_user_data,
    validate_pagination_params,
    username_validator,
    email_validator,
    password_validator
)
from .database import get_db_manager

__all__ = [
    # 认证和权限
    'login_required',
    'permission_required',
    'Permission',
    'RolePermission',
    
    # 异常处理
    'BaseAppException',
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'BusinessLogicError',
    
    # 工具函数
    'generate_uuid',
    'hash_password',
    'verify_password',
    
    # 常量
    'UserStatus',
    'UserRole',
    'LogLevel',
    'CacheKeys',
    'APIMessages',
    'ConfigDefaults',
    'HTTPStatus',
    'DateFormats',
    
    # 装饰器
    'log_execution_time',
    'handle_exceptions',
    'validate_json',
    'cache_result',
    'retry',
    
    # 验证器
    'validate_user_data',
    'validate_pagination_params',
    'username_validator',
    'email_validator',
    'password_validator',
    
    # 数据库管理
    'get_db_manager'
]