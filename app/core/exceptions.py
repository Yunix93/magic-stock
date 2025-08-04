"""
自定义异常类模块

定义应用程序使用的所有自定义异常
"""


class BaseAppException(Exception):
    """应用程序基础异常类"""
    
    def __init__(self, message, code=None, details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
            'details': self.details
        }


class AuthenticationError(BaseAppException):
    """认证异常"""
    
    def __init__(self, message="认证失败", code="AUTH_FAILED", details=None):
        super().__init__(message, code, details)


class AuthorizationError(BaseAppException):
    """授权异常"""
    
    def __init__(self, message="权限不足", code="PERMISSION_DENIED", details=None):
        super().__init__(message, code, details)


class ValidationError(BaseAppException):
    """数据验证异常"""
    
    def __init__(self, message="数据验证失败", code="VALIDATION_ERROR", details=None):
        super().__init__(message, code, details)


class BusinessLogicError(BaseAppException):
    """业务逻辑异常"""
    
    def __init__(self, message="业务逻辑错误", code="BUSINESS_ERROR", details=None):
        super().__init__(message, code, details)


class DatabaseError(BaseAppException):
    """数据库操作异常"""
    
    def __init__(self, message="数据库操作失败", code="DATABASE_ERROR", details=None):
        super().__init__(message, code, details)


class ConfigurationError(BaseAppException):
    """配置错误异常"""
    
    def __init__(self, message="配置错误", code="CONFIG_ERROR", details=None):
        super().__init__(message, code, details)


class ExternalServiceError(BaseAppException):
    """外部服务异常"""
    
    def __init__(self, message="外部服务错误", code="EXTERNAL_SERVICE_ERROR", details=None):
        super().__init__(message, code, details)


class RateLimitError(BaseAppException):
    """频率限制异常"""
    
    def __init__(self, message="请求过于频繁", code="RATE_LIMIT_EXCEEDED", details=None):
        super().__init__(message, code, details)


class FileOperationError(BaseAppException):
    """文件操作异常"""
    
    def __init__(self, message="文件操作失败", code="FILE_OPERATION_ERROR", details=None):
        super().__init__(message, code, details)