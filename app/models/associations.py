"""
关联表模型

定义用户-角色和角色-权限的多对多关系表
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.core.constants import DatabaseTables
import logging

logger = logging.getLogger(__name__)




class UserRole(BaseModel):
    """用户角色关联表"""
    
    __tablename__ = DatabaseTables.USER_ROLES
    
    # 外键字段
    user_id = Column( String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment="用户ID")
    role_id = Column( String(36), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, comment="角色ID")
    # 分配信息
    assigned_at = Column( DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, comment="分配时间")
    assigned_by = Column( String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment="分配者ID")
    
    # 关系定义
    # user = relationship("User", foreign_keys=[user_id])
    # role = relationship("Role", foreign_keys=[role_id])
    # assigner = relationship("User", foreign_keys=[assigned_by])
    
    # 索引和约束
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
        Index('idx_user_role_user', 'user_id'),
        Index('idx_user_role_role', 'role_id'),
        Index('idx_user_role_assigned', 'assigned_at'),
    )
    
    def __init__(self, **kwargs):
        """初始化用户角色关联"""
        kwargs.setdefault('assigned_at', datetime.now(timezone.utc))
        super().__init__(**kwargs)
    
    # 用户角色分配和移除逻辑已移至 UserService
    # 关联表模型只保留数据访问方法
    
    # 查询方法保留在模型层，但复杂业务逻辑移至服务层
    @classmethod
    def get_by_user_and_role(cls, user_id: str, role_id: str) -> Optional['UserRole']:
        """根据用户ID和角色ID获取关联"""
        return cls.filter_by(user_id=user_id, role_id=role_id).first()
    
    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class RolePermission(BaseModel):
    """角色权限关联表"""
    
    __tablename__ = DatabaseTables.ROLE_PERMISSIONS
    
    # 外键字段
    role_id = Column( String(36), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, comment="角色ID")
    permission_id = Column( String(36), ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, comment="权限ID")
    # 授权信息
    granted_at = Column( DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, comment="授权时间")
    granted_by = Column( String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment="授权者ID")
    
    # 关系定义
    # role = relationship("Role", foreign_keys=[role_id])
    # permission = relationship("Permission", foreign_keys=[permission_id])
    # granter = relationship("User", foreign_keys=[granted_by])
    
    # 索引和约束
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
        Index('idx_role_permission_role', 'role_id'),
        Index('idx_role_permission_permission', 'permission_id'),
        Index('idx_role_permission_granted', 'granted_at'),
    )
    
    def __init__(self, **kwargs):
        """初始化角色权限关联"""
        kwargs.setdefault('granted_at', datetime.now(timezone.utc))
        super().__init__(**kwargs)
    
    # 角色权限授予和撤销逻辑已移至 RoleService
    # 关联表模型只保留数据访问方法
    
    # 查询方法保留在模型层，但复杂业务逻辑移至服务层
    @classmethod
    def get_by_role_and_permission(cls, role_id: str, permission_id: str, session=None) -> Optional['RolePermission']:
        """根据角色ID和权限ID获取关联"""
        try:
            if session is None:
                return cls.filter_by(role_id=role_id, permission_id=permission_id).first()
            else:
                return session.query(cls).filter(
                    cls.role_id == role_id,
                    cls.permission_id == permission_id,
                    cls.is_deleted == False
                ).first()
        except Exception as e:
            return None
    
    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"