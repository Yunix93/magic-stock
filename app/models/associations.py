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
    user_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment="用户ID"
    )
    
    role_id = Column(
        String(36),
        ForeignKey('roles.id', ondelete='CASCADE'),
        nullable=False,
        comment="角色ID"
    )
    
    # 分配信息
    assigned_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="分配时间"
    )
    
    assigned_by = Column(
        String(36),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        comment="分配者ID"
    )
    
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
    
    @classmethod
    def assign_role_to_user(cls, user_id: str, role_id: str, assigned_by: str = None) -> 'UserRole':
        """为用户分配角色"""
        # 检查是否已存在
        existing = cls.get_by_user_and_role(user_id, role_id)
        if existing:
            logger.warning(f"用户 {user_id} 已拥有角色 {role_id}")
            return existing
        
        # 创建新的关联
        user_role = cls(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by
        )
        
        user_role.save()
        
        logger.info(f"为用户 {user_id} 分配角色 {role_id}")
        return user_role
    
    @classmethod
    def remove_role_from_user(cls, user_id: str, role_id: str) -> bool:
        """从用户移除角色"""
        user_role = cls.get_by_user_and_role(user_id, role_id)
        if not user_role:
            logger.warning(f"用户 {user_id} 不拥有角色 {role_id}")
            return False
        
        user_role.delete(soft=False)
        
        logger.info(f"从用户 {user_id} 移除角色 {role_id}")
        return True
    
    @classmethod
    def get_by_user_and_role(cls, user_id: str, role_id: str) -> Optional['UserRole']:
        """根据用户ID和角色ID获取关联"""
        return cls.filter_by(user_id=user_id, role_id=role_id).first()
    
    @classmethod
    def get_roles_by_user(cls, user_id: str, session=None) -> List['Role']:
        """获取用户的所有角色"""
        try:
            # 延迟导入避免循环依赖
            import importlib
            role_module = importlib.import_module('app.models.role')
            Role = role_module.Role
            
            if session is None:
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                roles = session.query(Role).join(
                    cls, Role.id == cls.role_id
                ).filter(
                    cls.user_id == user_id,
                    cls.is_deleted == False,
                    Role.is_deleted == False
                ).all()
                
                return roles
            finally:
                if should_close:
                    session.close()
        except Exception as e:
            return []
    
    @classmethod
    def get_users_by_role(cls, role_id: str, session=None) -> List['User']:
        """获取拥有指定角色的所有用户"""
        try:
            # 延迟导入避免循环依赖
            import importlib
            user_module = importlib.import_module('app.models.user')
            User = user_module.User
            
            if session is None:
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                users = session.query(User).join(
                cls, User.id == cls.user_id
            ).filter(
                cls.role_id == role_id,
                cls.is_deleted == False,
                User.is_deleted == False
            ).all()
                
                return users
            finally:
                session.close()
        except Exception as e:
            return []
    
    @classmethod
    def count_users_by_role(cls, role_id: str, session=None) -> int:
        """统计拥有指定角色的用户数量"""
        try:
            if session is None:
                # 延迟导入避免循环依赖
                import importlib
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                count = session.query(cls).filter(
                    cls.role_id == role_id,
                    cls.is_deleted == False
                ).count()
                
                return count
            finally:
                if should_close:
                    session.close()
        except Exception as e:
            return 0
    
    @classmethod
    def user_has_role(cls, user_id: str, role_name: str, session=None) -> bool:
        """检查用户是否拥有指定角色"""
        try:
            # 延迟导入避免循环依赖
            import importlib
            role_module = importlib.import_module('app.models.role')
            Role = role_module.Role
            
            if session is None:
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                exists = session.query(cls).join(
                    Role, Role.id == cls.role_id
                ).filter(
                    cls.user_id == user_id,
                    Role.name == role_name,
                    cls.is_deleted == False,
                    Role.is_deleted == False
                ).first()
                
                return exists is not None
            finally:
                if should_close:
                    session.close()
        except Exception as e:
            return False
    
    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class RolePermission(BaseModel):
    """角色权限关联表"""
    
    __tablename__ = DatabaseTables.ROLE_PERMISSIONS
    
    # 外键字段
    role_id = Column(
        String(36),
        ForeignKey('roles.id', ondelete='CASCADE'),
        nullable=False,
        comment="角色ID"
    )
    
    permission_id = Column(
        String(36),
        ForeignKey('permissions.id', ondelete='CASCADE'),
        nullable=False,
        comment="权限ID"
    )
    
    # 授权信息
    granted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="授权时间"
    )
    
    granted_by = Column(
        String(36),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        comment="授权者ID"
    )
    
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
    
    @classmethod
    def grant_permission_to_role(cls, role_id: str, permission_id: str, granted_by: str = None) -> 'RolePermission':
        """为角色授予权限"""
        # 检查是否已存在
        existing = cls.get_by_role_and_permission(role_id, permission_id)
        if existing:
            logger.warning(f"角色 {role_id} 已拥有权限 {permission_id}")
            return existing
        
        # 创建新的关联
        role_permission = cls(
            role_id=role_id,
            permission_id=permission_id,
            granted_by=granted_by
        )
        
        role_permission.save()
        
        logger.info(f"为角色 {role_id} 授予权限 {permission_id}")
        return role_permission
    
    @classmethod
    def revoke_permission_from_role(cls, role_id: str, permission_id: str) -> bool:
        """从角色撤销权限"""
        role_permission = cls.get_by_role_and_permission(role_id, permission_id)
        if not role_permission:
            logger.warning(f"角色 {role_id} 不拥有权限 {permission_id}")
            return False
        
        role_permission.delete(soft=False)
        
        logger.info(f"从角色 {role_id} 撤销权限 {permission_id}")
        return True
    
    @classmethod
    def get_by_role_and_permission(cls, role_id: str, permission_id: str, session=None) -> Optional['RolePermission']:
        """根据角色ID和权限ID获取关联"""
        if session is None:
            return cls.filter_by(role_id=role_id, permission_id=permission_id).first()
        else:
            return session.query(cls).filter(
                cls.role_id == role_id,
                cls.permission_id == permission_id,
                cls.is_deleted == False
            ).first()
    
    @classmethod
    def get_permissions_by_role(cls, role_id: str, session=None) -> List['Permission']:
        """获取角色的所有权限"""
        try:
            # 延迟导入避免循环依赖
            import importlib
            permission_module = importlib.import_module('app.models.permission')
            Permission = permission_module.Permission
            
            if session is None:
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                permissions = session.query(Permission).join(
                    cls, Permission.id == cls.permission_id
                ).filter(
                    cls.role_id == role_id,
                    cls.is_deleted == False,
                    Permission.is_deleted == False
                ).all()
                
                return permissions
            finally:
                if should_close:
                    session.close()
        except Exception as e:
            return []
    
    @classmethod
    def get_roles_by_permission(cls, permission_id: str, session=None) -> List['Role']:
        """获取拥有指定权限的所有角色"""
        try:
            # 延迟导入避免循环依赖
            import importlib
            role_module = importlib.import_module('app.models.role')
            Role = role_module.Role
            
            if session is None:
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                roles = session.query(Role).join(
                    cls, Role.id == cls.role_id
                ).filter(
                    cls.permission_id == permission_id,
                    cls.is_deleted == False,
                    Role.is_deleted == False
                ).all()
                
                return roles
            finally:
                if should_close:
                    session.close()
        except Exception as e:
            return []
    
    @classmethod
    def count_roles_by_permission(cls, permission_id: str, session=None) -> int:
        """统计拥有指定权限的角色数量"""
        try:
            if session is None:
                # 延迟导入避免循环依赖
                import importlib
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                count = session.query(cls).filter(
                    cls.permission_id == permission_id,
                    cls.is_deleted == False
                ).count()
                
                return count
            finally:
                if should_close:
                    session.close()
        except Exception as e:
            return 0
    
    @classmethod
    def role_has_permission(cls, role_id: str, permission_name: str, session=None) -> bool:
        """检查角色是否拥有指定权限"""
        try:
            # 延迟导入避免循环依赖
            import importlib
            permission_module = importlib.import_module('app.models.permission')
            Permission = permission_module.Permission
            
            if session is None:
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                exists = session.query(cls).join(
                    Permission, Permission.id == cls.permission_id
                ).filter(
                    cls.role_id == role_id,
                    Permission.name == permission_name,
                    cls.is_deleted == False,
                    Permission.is_deleted == False
                ).first()
                
                return exists is not None
            finally:
                if should_close:
                    session.close()
        except Exception as e:
            return False
    
    @classmethod
    def user_has_permission(cls, user_id: str, permission_name: str, session=None) -> bool:
        """检查用户是否通过角色拥有指定权限"""
        try:
            # 延迟导入避免循环依赖
            import importlib
            permission_module = importlib.import_module('app.models.permission')
            Permission = permission_module.Permission
            
            if session is None:
                database_module = importlib.import_module('app.core.database')
                session = database_module.get_session()
                should_close = True
            else:
                should_close = False
            
            try:
                # 通过用户角色关联和角色权限关联查询
                exists = session.query(cls).join(
                    Permission, Permission.id == cls.permission_id
                ).join(
                    UserRole, UserRole.role_id == cls.role_id
                ).filter(
                    UserRole.user_id == user_id,
                    Permission.name == permission_name,
                    cls.is_deleted == False,
                    UserRole.is_deleted == False,
                    Permission.is_deleted == False
                ).first()
                
                return exists is not None
            finally:
                if should_close:
                    session.close()
        except Exception as e:
            return False
    
    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"