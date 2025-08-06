"""
用户数据模型

定义用户相关的数据模型和业务逻辑
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Boolean, DateTime, Text, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.core.utils import hash_password, verify_password, generate_secure_token
from app.core.validators import validate_user_data, username_validator, email_validator, password_validator
from app.core.constants import UserStatus, DatabaseTables
from app.core.exceptions import ValidationError, AuthenticationError
import logging

logger = logging.getLogger(__name__)


class User(BaseModel):
    """用户模型"""
    
    __tablename__ = DatabaseTables.USERS
    
    # 基本信息字段
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名"
    )
    
    email = Column(
        String(254),
        unique=True,
        nullable=False,
        index=True,
        comment="邮箱地址"
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        comment="密码哈希值"
    )
    
    full_name = Column(
        String(100),
        nullable=True,
        comment="真实姓名"
    )
    
    # 状态管理字段
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已验证邮箱"
    )
    
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为超级管理员"
    )
    
    # 时间戳字段
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )
    
    password_changed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="密码修改时间"
    )
    
    # 安全字段
    failed_login_attempts = Column(
        String(10),
        default="0",
        nullable=False,
        comment="失败登录次数"
    )
    
    locked_until = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="账户锁定到期时间"
    )
    
    # 扩展信息字段
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="头像URL"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        comment="手机号码"
    )
    
    bio = Column(
        Text,
        nullable=True,
        comment="个人简介"
    )
    
    # 系统字段
    verification_token = Column(
        String(255),
        nullable=True,
        comment="邮箱验证令牌"
    )
    
    reset_token = Column(
        String(255),
        nullable=True,
        comment="密码重置令牌"
    )
    
    reset_token_expires = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="重置令牌过期时间"
    )
    
    # 关系定义
    # roles = relationship("Role", secondary="user_roles", back_populates="users")
    login_logs = relationship("LoginLog", back_populates="user", cascade="all, delete-orphan")
    operation_logs = relationship("OperationLog", back_populates="user", cascade="all, delete-orphan")
    
    # 索引定义
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
        Index('idx_user_active', 'is_active'),
        Index('idx_user_last_login', 'last_login'),
    )
    
    def __init__(self, **kwargs):
        """初始化用户实例"""
        # 设置默认值
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_verified', False)
        kwargs.setdefault('is_superuser', False)
        kwargs.setdefault('failed_login_attempts', "0")
        
        # 验证必要字段
        if 'username' in kwargs:
            kwargs['username'] = username_validator.validate(kwargs['username'], '用户名')
        
        if 'email' in kwargs:
            kwargs['email'] = email_validator.validate(kwargs['email'], '邮箱')
        
        # 处理密码
        if 'password' in kwargs:
            password = kwargs.pop('password')
            # 先调用父类初始化，然后设置密码
            super().__init__(**kwargs)
            self.set_password(password)
            return
        
        super().__init__(**kwargs)
    
    def check_password(self, password: str) -> bool:
        """验证密码 - 基本验证方法，保留在模型层"""
        if not self.password_hash:
            return False
        
        return verify_password(password, self.password_hash)
    
    def is_locked(self) -> bool:
        """检查账户是否被锁定 - 基本状态检查，保留在模型层"""
        if not self.locked_until:
            return False
        
        return datetime.now(timezone.utc) < self.locked_until
    
    def verify_reset_token(self, token: str) -> bool:
        """验证重置令牌 - 基本验证方法，保留在模型层"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        if datetime.now(timezone.utc) > self.reset_token_expires:
            return False
        
        return self.reset_token == token
    
    # 复杂的业务逻辑方法已移至 UserService
    # 包括：用户认证、密码管理、状态管理、角色管理等
    
    def get_status(self) -> str:
        """获取用户状态 - 基本状态计算，保留在模型层"""
        if not self.is_active:
            return UserStatus.INACTIVE.value
        elif self.is_locked():
            return UserStatus.LOCKED.value
        elif not self.is_verified:
            return UserStatus.PENDING.value
        else:
            return UserStatus.ACTIVE.value
    
    def to_dict(self, exclude_fields: List[str] = None, include_sensitive: bool = False) -> Dict[str, Any]:
        """转换为字典格式"""
        # 默认排除敏感字段
        default_exclude = ['password_hash', 'verification_token', 'reset_token']
        if not include_sensitive:
            exclude_fields = (exclude_fields or []) + default_exclude
        
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加计算字段
        result['status'] = self.get_status()
        result['is_locked'] = self.is_locked()
        result['failed_attempts'] = int(self.failed_login_attempts or "0")
        
        return result
    
    def to_public_dict(self) -> Dict[str, Any]:
        """转换为公开信息字典（用于API响应）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'status': self.get_status(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    # 用户创建逻辑已移至 UserService.create_user()
    
    # 查询方法保留在模型层，但复杂业务逻辑移至服务层
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """根据用户名获取用户"""
        try:
            return cls.filter_by(username=username).first()
        except:
            return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """根据邮箱获取用户"""
        try:
            return cls.filter_by(email=email.lower()).first()
        except:
            return None
    
    # 角色和权限管理方法已移至 UserService
    # 模型层只保留数据访问和基本验证方法
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"