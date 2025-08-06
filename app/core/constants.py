"""
系统常量定义

定义系统中使用的所有常量
"""

from enum import Enum


class UserStatus(Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    LOCKED = "locked"
    DELETED = "deleted"


class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class RoleType(Enum):
    """角色类型枚举"""
    SYSTEM = "system"
    CUSTOM = "custom"


class PermissionType(Enum):
    """权限类型枚举"""
    SYSTEM = "system"
    CUSTOM = "custom"


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CacheKeys:
    """缓存键名常量"""
    USER_PREFIX = "user:"
    ROLE_PREFIX = "role:"
    PERMISSION_PREFIX = "permission:"
    SESSION_PREFIX = "session:"
    
    @classmethod
    def user_key(cls, user_id):
        return f"{cls.USER_PREFIX}{user_id}"
    
    @classmethod
    def role_key(cls, role_id):
        return f"{cls.ROLE_PREFIX}{role_id}"
    
    @classmethod
    def session_key(cls, session_id):
        return f"{cls.SESSION_PREFIX}{session_id}"


class APIMessages:
    """API响应消息常量"""
    SUCCESS = "操作成功"
    CREATED = "创建成功"
    UPDATED = "更新成功"
    DELETED = "删除成功"
    
    # 错误消息
    INVALID_REQUEST = "请求参数无效"
    UNAUTHORIZED = "未授权访问"
    FORBIDDEN = "权限不足"
    NOT_FOUND = "资源不存在"
    CONFLICT = "资源冲突"
    INTERNAL_ERROR = "服务器内部错误"
    
    # 用户相关
    USER_NOT_FOUND = "用户不存在"
    USER_EXISTS = "用户已存在"
    INVALID_CREDENTIALS = "用户名或密码错误"
    PASSWORD_TOO_WEAK = "密码强度不足"
    
    # 权限相关
    ROLE_NOT_FOUND = "角色不存在"
    PERMISSION_DENIED = "权限不足"


class DatabaseTables:
    """数据库表名常量"""
    USERS = "users"
    ROLES = "roles"
    PERMISSIONS = "permissions"
    USER_ROLES = "user_roles"
    ROLE_PERMISSIONS = "role_permissions"
    LOGIN_LOGS = "login_logs"
    OPERATION_LOGS = "operation_logs"


class ConfigDefaults:
    """配置默认值常量"""
    # 分页
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 密码策略
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # 会话
    SESSION_TIMEOUT = 3600  # 1小时
    REMEMBER_ME_DURATION = 2592000  # 30天
    
    # 文件上传
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'csv'}
    
    # API限制
    DEFAULT_RATE_LIMIT = "100/hour"
    
    # 缓存
    DEFAULT_CACHE_TIMEOUT = 300  # 5分钟


class HTTPStatus:
    """HTTP状态码常量"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


class DateFormats:
    """日期格式常量"""
    DATETIME = "%Y-%m-%d %H:%M:%S"
    DATE = "%Y-%m-%d"
    TIME = "%H:%M:%S"
    ISO_DATETIME = "%Y-%m-%dT%H:%M:%S.%fZ"
    DISPLAY_DATETIME = "%Y年%m月%d日 %H:%M"
    DISPLAY_DATE = "%Y年%m月%d日"