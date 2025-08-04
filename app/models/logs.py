"""
日志记录数据模型

定义登录日志和操作日志的数据模型
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Boolean, Index, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.core.validators import StringValidator
from app.core.exceptions import ValidationError
import logging
import json

logger = logging.getLogger(__name__)


class LoginLog(BaseModel):
    """登录日志模型"""
    
    __tablename__ = "login_logs"
    
    # 用户信息
    user_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="用户ID"
    )
    
    # 登录信息
    ip_address = Column(
        String(45),  # IPv6最大长度
        nullable=True,
        index=True,
        comment="IP地址"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="用户代理字符串"
    )
    
    status = Column(
        String(20),
        nullable=False,
        index=True,
        comment="登录状态：success, failed"
    )
    
    login_time = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="登录时间"
    )
    
    logout_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="登出时间"
    )
    
    # 关系定义
    user = relationship("User", back_populates="login_logs")
    
    # 索引定义
    __table_args__ = (
        Index('idx_login_log_user', 'user_id'),
        Index('idx_login_log_time', 'login_time'),
        Index('idx_login_log_ip', 'ip_address'),
        Index('idx_login_log_status', 'status'),
    )
    
    def __init__(self, **kwargs):
        """初始化登录日志实例"""
        # 设置默认值
        kwargs.setdefault('login_time', datetime.now(timezone.utc))
        kwargs.setdefault('status', 'failed')
        
        # 验证状态字段
        if 'status' in kwargs:
            if kwargs['status'] not in ['success', 'failed']:
                raise ValidationError("登录状态必须是 'success' 或 'failed'")
        
        super().__init__(**kwargs)
    
    def set_logout(self):
        """设置登出时间"""
        self.logout_time = datetime.now(timezone.utc)
        logger.info(f"用户 {self.user_id} 登出")
    
    def get_session_duration(self) -> Optional[int]:
        """获取会话持续时间（秒）"""
        if not self.logout_time or not self.login_time:
            return None
        
        # 确保两个时间都有时区信息
        login_time = self.login_time
        logout_time = self.logout_time
        
        # 如果时间没有时区信息，假设为UTC
        if login_time.tzinfo is None:
            login_time = login_time.replace(tzinfo=timezone.utc)
        if logout_time.tzinfo is None:
            logout_time = logout_time.replace(tzinfo=timezone.utc)
        
        duration = (logout_time - login_time).total_seconds()
        return int(duration)
    
    def get_session_duration_formatted(self) -> str:
        """获取格式化的会话持续时间"""
        duration = self.get_session_duration()
        if duration is None:
            return "进行中"
        
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟{seconds}秒"
        elif minutes > 0:
            return f"{minutes}分钟{seconds}秒"
        else:
            return f"{seconds}秒"
    
    def to_dict(self, exclude_fields: List[str] = None) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加计算字段
        result['session_duration'] = self.get_session_duration()
        result['session_duration_formatted'] = self.get_session_duration_formatted()
        
        return result
    
    @classmethod
    def create_login_log(cls, user_id: str = None, ip_address: str = None, 
                        user_agent: str = None, status: str = 'failed') -> 'LoginLog':
        """创建登录日志"""
        log = cls(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        
        log.save()
        
        log_type = "成功" if status == 'success' else "失败"
        logger.info(f"创建登录日志: 用户 {user_id} 登录{log_type}")
        return log
    
    @classmethod
    def get_by_user(cls, user_id: str, limit: int = 50) -> List['LoginLog']:
        """获取用户的登录日志"""
        return cls.filter_by(user_id=user_id).order_by(
            cls.login_time.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_recent_logs(cls, hours: int = 24, limit: int = 100) -> List['LoginLog']:
        """获取最近的登录日志"""
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return cls.filter_by().filter(
            cls.login_time >= cutoff_time
        ).order_by(
            cls.login_time.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_failed_attempts(cls, user_id: str = None, ip_address: str = None, 
                           hours: int = 1) -> List['LoginLog']:
        """获取失败的登录尝试"""
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = cls.filter_by(status='failed').filter(
            cls.login_time >= cutoff_time
        )
        
        if user_id:
            query = query.filter(cls.user_id == user_id)
        
        if ip_address:
            query = query.filter(cls.ip_address == ip_address)
        
        return query.order_by(cls.login_time.desc()).all()
    
    def __repr__(self):
        return f"<LoginLog(user_id={self.user_id}, status={self.status}, time={self.login_time})>"


class OperationLog(BaseModel):
    """操作日志模型"""
    
    __tablename__ = "operation_logs"
    
    # 用户信息
    user_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="操作用户ID"
    )
    
    # 操作信息
    operation = Column(
        String(50),
        nullable=False,
        index=True,
        comment="操作类型"
    )
    
    resource = Column(
        String(50),
        nullable=False,
        index=True,
        comment="操作资源"
    )
    
    details = Column(
        JSON,
        nullable=True,
        comment="操作详情（JSON格式）"
    )
    
    # 客户端信息
    ip_address = Column(
        String(45),
        nullable=True,
        index=True,
        comment="客户端IP地址"
    )
    
    # 时间信息
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="操作时间"
    )
    
    # 关系定义
    user = relationship("User", back_populates="operation_logs")
    
    # 索引定义
    __table_args__ = (
        Index('idx_operation_log_user', 'user_id'),
        Index('idx_operation_log_operation', 'operation'),
        Index('idx_operation_log_resource', 'resource'),
        Index('idx_operation_log_time', 'created_at'),
        Index('idx_operation_log_ip', 'ip_address'),
    )
    
    def __init__(self, **kwargs):
        """初始化操作日志实例"""
        # 设置默认值
        kwargs.setdefault('created_at', datetime.now(timezone.utc))
        
        # 验证必要字段
        if 'operation' in kwargs:
            operation_validator = StringValidator(min_length=1, max_length=50)
            kwargs['operation'] = operation_validator.validate(kwargs['operation'], '操作类型')
        
        if 'resource' in kwargs:
            resource_validator = StringValidator(min_length=1, max_length=50)
            kwargs['resource'] = resource_validator.validate(kwargs['resource'], '操作资源')
        
        super().__init__(**kwargs)
    
    def set_details(self, details: Dict[str, Any]):
        """设置操作详情"""
        self.details = details
    
    def get_details(self) -> Dict[str, Any]:
        """获取操作详情"""
        return self.details or {}
    
    def to_dict(self, exclude_fields: List[str] = None) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 确保details字段正确序列化
        result['details'] = self.get_details()
        
        return result
    
    @classmethod
    def create_operation_log(cls, user_id: str = None, operation: str = None, 
                           resource: str = None, details: Dict[str, Any] = None,
                           ip_address: str = None) -> 'OperationLog':
        """创建操作日志"""
        if not operation:
            raise ValidationError("操作类型不能为空")
        
        if not resource:
            raise ValidationError("操作资源不能为空")
        
        log = cls(
            user_id=user_id,
            operation=operation,
            resource=resource,
            details=details,
            ip_address=ip_address
        )
        
        log.save()
        
        logger.info(f"创建操作日志: 用户 {user_id} {operation} {resource}")
        return log
    
    @classmethod
    def get_by_user(cls, user_id: str, limit: int = 50) -> List['OperationLog']:
        """获取用户的操作日志"""
        return cls.filter_by(user_id=user_id).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_resource(cls, resource: str, limit: int = 50) -> List['OperationLog']:
        """获取资源的操作日志"""
        return cls.filter_by(resource=resource).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_operation(cls, operation: str, limit: int = 50) -> List['OperationLog']:
        """获取指定操作类型的日志"""
        return cls.filter_by(operation=operation).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_recent_logs(cls, hours: int = 24, limit: int = 100) -> List['OperationLog']:
        """获取最近的操作日志"""
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return cls.filter_by().filter(
            cls.created_at >= cutoff_time
        ).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def search_logs(cls, query: str, limit: int = 50) -> List['OperationLog']:
        """搜索操作日志"""
        from sqlalchemy import or_
        
        search_filter = or_(
            cls.operation.ilike(f'%{query}%'),
            cls.resource.ilike(f'%{query}%')
        )
        
        return cls.filter_by().filter(search_filter).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    def __repr__(self):
        return f"<OperationLog(user_id={self.user_id}, operation={self.operation}, resource={self.resource})>"