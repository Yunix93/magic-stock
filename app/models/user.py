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
    
    def set_password(self, password: str) -> str:
        """设置密码"""
        # 验证密码强度
        password_validator.validate(password, '密码')
        
        # 生成密码哈希
        password_hash = hash_password(password)
        self.password_hash = password_hash
        self.password_changed_at = datetime.now(timezone.utc)
        
        # 清除重置令牌
        self.reset_token = None
        self.reset_token_expires = None
        
        logger.info(f"用户 {self.username} 密码已更新")
        return password_hash
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        if not self.password_hash:
            return False
        
        return verify_password(password, self.password_hash)
    
    def authenticate(self, password: str) -> bool:
        """用户认证"""
        # 检查账户状态
        if not self.is_active:
            raise AuthenticationError("账户已被禁用")
        
        if self.is_locked():
            raise AuthenticationError("账户已被锁定")
        
        # 验证密码
        if not self.check_password(password):
            self.increment_failed_attempts()
            raise AuthenticationError("密码错误")
        
        # 认证成功，重置失败次数
        self.reset_failed_attempts()
        self.update_last_login()
        
        logger.info(f"用户 {self.username} 认证成功")
        return True
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.now(timezone.utc)
    
    def increment_failed_attempts(self):
        """增加失败登录次数"""
        try:
            attempts = int(self.failed_login_attempts or "0")
        except ValueError:
            attempts = 0
        
        attempts += 1
        self.failed_login_attempts = str(attempts)
        
        # 如果失败次数过多，锁定账户
        max_attempts = 5  # 可以从配置中读取
        if attempts >= max_attempts:
            self.lock_account(minutes=30)  # 锁定30分钟
        
        logger.warning(f"用户 {self.username} 登录失败，失败次数: {attempts}")
    
    def reset_failed_attempts(self):
        """重置失败登录次数"""
        self.failed_login_attempts = "0"
        self.locked_until = None
    
    def lock_account(self, minutes: int = 30):
        """锁定账户"""
        from datetime import timedelta
        self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        logger.warning(f"用户 {self.username} 账户已锁定 {minutes} 分钟")
    
    def unlock_account(self):
        """解锁账户"""
        self.locked_until = None
        self.reset_failed_attempts()
        logger.info(f"用户 {self.username} 账户已解锁")
    
    def is_locked(self) -> bool:
        """检查账户是否被锁定"""
        if not self.locked_until:
            return False
        
        return datetime.now(timezone.utc) < self.locked_until
    
    def activate(self):
        """激活用户"""
        self.is_active = True
        self.unlock_account()
        logger.info(f"用户 {self.username} 已激活")
    
    def deactivate(self):
        """停用用户"""
        self.is_active = False
        logger.info(f"用户 {self.username} 已停用")
    
    def verify_email(self):
        """验证邮箱"""
        self.is_verified = True
        self.verification_token = None
        logger.info(f"用户 {self.username} 邮箱已验证")
    
    def generate_verification_token(self) -> str:
        """生成邮箱验证令牌"""
        token = generate_secure_token()
        self.verification_token = token
        return token
    
    def generate_reset_token(self, expires_in: int = 3600) -> str:
        """生成密码重置令牌"""
        from datetime import timedelta
        token = generate_secure_token()
        self.reset_token = token
        self.reset_token_expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return token
    
    def verify_reset_token(self, token: str) -> bool:
        """验证重置令牌"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        if datetime.now(timezone.utc) > self.reset_token_expires:
            return False
        
        return self.reset_token == token
    
    def get_status(self) -> str:
        """获取用户状态"""
        if not self.is_active:
            return UserStatus.INACTIVE.value
        elif self.is_locked():
            return UserStatus.SUSPENDED.value
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
    
    @classmethod
    def create_user(cls, username: str, email: str, password: str, **kwargs) -> 'User':
        """创建新用户"""
        # 验证用户名和邮箱唯一性
        existing_user = cls.get_by_username(username)
        if existing_user:
            raise ValidationError("用户名已存在")
        
        existing_email = cls.get_by_email(email)
        if existing_email:
            raise ValidationError("邮箱已存在")
        
        # 创建用户实例
        user = cls(
            username=username,
            email=email,
            password=password,
            **kwargs
        )
        
        # 生成验证令牌
        user.generate_verification_token()
        
        # 保存到数据库
        user.save()
        
        logger.info(f"新用户创建成功: {username}")
        return user
    
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
    
    @classmethod
    def get_active_users(cls) -> List['User']:
        """获取所有活跃用户"""
        return cls.filter_by(is_active=True).all()
    
    @classmethod
    def search_users(cls, query: str, limit: int = 20) -> List['User']:
        """搜索用户"""
        from sqlalchemy import or_
        
        search_filter = or_(
            cls.username.ilike(f'%{query}%'),
            cls.email.ilike(f'%{query}%'),
            cls.full_name.ilike(f'%{query}%')
        )
        
        return cls.filter_by().filter(search_filter).limit(limit).all()
    
    def add_role(self, role, assigned_by: str = None) -> bool:
        """为用户添加角色"""
        from app.models.role import Role
        from app.models.associations import UserRole
        
        if isinstance(role, str):
            # 如果传入的是角色名称，查找角色对象
            role_obj = Role.get_by_name(role)
            if not role_obj:
                raise ValidationError(f"角色 {role} 不存在")
            role = role_obj
        
        if not isinstance(role, Role):
            raise ValidationError("角色对象类型错误")
        
        # 创建用户角色关联
        user_role = UserRole.assign_role_to_user(self.id, role.id, assigned_by)
        return user_role is not None
    
    def remove_role(self, role) -> bool:
        """从用户移除角色"""
        from app.models.role import Role
        from app.models.associations import UserRole
        
        if isinstance(role, str):
            # 如果传入的是角色名称，查找角色对象
            role_obj = Role.get_by_name(role)
            if not role_obj:
                raise ValidationError(f"角色 {role} 不存在")
            role = role_obj
        
        if not isinstance(role, Role):
            raise ValidationError("角色对象类型错误")
        
        return UserRole.remove_role_from_user(self.id, role.id)
    
    def has_role(self, role_name: str) -> bool:
        """检查用户是否拥有指定角色"""
        from app.models.associations import UserRole
        
        return UserRole.user_has_role(self.id, role_name)
    
    def has_permission(self, permission_name: str) -> bool:
        """检查用户是否拥有指定权限"""
        from app.models.associations import RolePermission
        
        return RolePermission.user_has_permission(self.id, permission_name)
    
    def get_roles(self) -> List['Role']:
        """获取用户的所有角色"""
        from app.models.associations import UserRole
        
        return UserRole.get_roles_by_user(self.id)
    
    def get_permissions(self) -> List['Permission']:
        """获取用户通过角色拥有的所有权限"""
        from app.models.associations import RolePermission
        
        # 获取用户的所有角色
        roles = self.get_roles()
        
        # 获取这些角色的所有权限
        permissions = []
        for role in roles:
            role_permissions = RolePermission.get_permissions_by_role(role.id)
            permissions.extend(role_permissions)
        
        # 去重
        unique_permissions = []
        seen_ids = set()
        for permission in permissions:
            if permission.id not in seen_ids:
                unique_permissions.append(permission)
                seen_ids.add(permission.id)
        
        return unique_permissions
    
    def is_admin(self) -> bool:
        """检查用户是否为管理员"""
        return self.has_role('admin') or self.is_superuser
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"