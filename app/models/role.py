"""
角色数据模型

定义角色相关的数据模型和业务逻辑
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Boolean, Text, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.core.validators import StringValidator
from app.core.constants import DatabaseTables
from app.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class Role(BaseModel):
    """角色模型"""
    
    __tablename__ = DatabaseTables.ROLES
    
    # 基本信息字段
    name = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="角色名称"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="角色描述"
    )
    
    # 状态字段
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 系统字段
    is_system = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为系统角色"
    )
    
    # 排序字段
    sort_order = Column(
        String(10),
        default="0",
        nullable=False,
        comment="排序顺序"
    )
    
    # 关系定义
    # users = relationship("User", secondary="user_roles", back_populates="roles")
    # permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    
    # 索引定义
    __table_args__ = (
        Index('idx_role_name', 'name'),
        Index('idx_role_active', 'is_active'),
        Index('idx_role_system', 'is_system'),
    )
    
    def __init__(self, **kwargs):
        """初始化角色实例"""
        # 设置默认值
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_system', False)
        kwargs.setdefault('sort_order', "0")
        
        # 验证角色名称
        if 'name' in kwargs:
            name_validator = StringValidator(min_length=2, max_length=50)
            kwargs['name'] = name_validator.validate(kwargs['name'], '角色名称')
        
        super().__init__(**kwargs)
    
    def activate(self):
        """激活角色"""
        self.is_active = True
        logger.info(f"角色 {self.name} 已激活")
    
    def deactivate(self):
        """停用角色"""
        if self.is_system:
            raise ValidationError("系统角色不能被停用")
        
        self.is_active = False
        logger.info(f"角色 {self.name} 已停用")
    
    def add_permission(self, permission, session=None):
        """添加权限"""
        # 延迟导入避免循环依赖
        import importlib
        permission_module = importlib.import_module('app.models.permission')
        associations_module = importlib.import_module('app.models.associations')
        
        Permission = permission_module.Permission
        RolePermission = associations_module.RolePermission
        
        if not isinstance(permission, Permission):
            raise ValidationError("权限对象类型错误")
        
        # 检查权限是否已存在
        existing = RolePermission.get_by_role_and_permission(self.id, permission.id, session=session)
        if existing:
            logger.warning(f"角色 {self.name} 已拥有权限 {permission.name}")
            return False
        
        # 创建角色权限关联
        role_permission = RolePermission.grant_permission_to_role(self.id, permission.id, session=session)
        
        logger.info(f"为角色 {self.name} 添加权限 {permission.name}")
        return True
    
    def remove_permission(self, permission, session=None):
        """移除权限"""
        # 延迟导入避免循环依赖
        import importlib
        permission_module = importlib.import_module('app.models.permission')
        associations_module = importlib.import_module('app.models.associations')
        
        Permission = permission_module.Permission
        RolePermission = associations_module.RolePermission
        
        if not isinstance(permission, Permission):
            raise ValidationError("权限对象类型错误")
        
        # 查找角色权限关联
        role_permission = RolePermission.get_by_role_and_permission(self.id, permission.id, session=session)
        if not role_permission:
            logger.warning(f"角色 {self.name} 不拥有权限 {permission.name}")
            return False
        
        # 删除关联
        role_permission.delete(soft=False, session=session)
        
        logger.info(f"从角色 {self.name} 移除权限 {permission.name}")
        return True
    
    def has_permission(self, permission_name: str, session=None) -> bool:
        """检查是否拥有指定权限"""
        # 延迟导入避免循环依赖
        import importlib
        associations_module = importlib.import_module('app.models.associations')
        RolePermission = associations_module.RolePermission
        
        return RolePermission.role_has_permission(self.id, permission_name, session=session)
    
    def get_permissions(self, session=None) -> List['Permission']:
        """获取角色的所有权限"""
        # 延迟导入避免循环依赖
        import importlib
        associations_module = importlib.import_module('app.models.associations')
        RolePermission = associations_module.RolePermission
        
        return RolePermission.get_permissions_by_role(self.id, session=session)
    
    def get_users(self, session=None) -> List['User']:
        """获取拥有此角色的所有用户"""
        # 延迟导入避免循环依赖
        import importlib
        associations_module = importlib.import_module('app.models.associations')
        UserRole = associations_module.UserRole
        
        return UserRole.get_users_by_role(self.id, session=session)
    
    def get_user_count(self, session=None) -> int:
        """获取拥有此角色的用户数量"""
        # 延迟导入避免循环依赖
        import importlib
        associations_module = importlib.import_module('app.models.associations')
        UserRole = associations_module.UserRole
        
        return UserRole.count_users_by_role(self.id, session=session)
    
    def can_be_deleted(self) -> bool:
        """检查角色是否可以被删除"""
        if self.is_system:
            return False
        
        # 检查是否有用户使用此角色
        user_count = self.get_user_count()
        return user_count == 0
    
    def to_dict(self, exclude_fields: List[str] = None, include_permissions: bool = False) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加计算字段
        result['user_count'] = self.get_user_count()
        result['can_be_deleted'] = self.can_be_deleted()
        
        # 包含权限信息
        if include_permissions:
            permissions = self.get_permissions()
            result['permissions'] = [p.to_dict() for p in permissions]
        
        return result
    
    def to_public_dict(self) -> Dict[str, Any]:
        """转换为公开信息字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'is_system': self.is_system,
            'sort_order': int(self.sort_order or "0"),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_role(cls, name: str, description: str = None, **kwargs) -> 'Role':
        """创建新角色"""
        # 验证角色名称唯一性
        if cls.get_by_name(name):
            raise ValidationError("角色名称已存在")
        
        # 创建角色实例
        role = cls(
            name=name,
            description=description,
            **kwargs
        )
        
        # 保存到数据库
        role.save()
        
        logger.info(f"新角色创建成功: {name}")
        return role
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Role']:
        """根据角色名称获取角色"""
        try:
            return cls.filter_by(name=name).first()
        except:
            return None
    
    @classmethod
    def get_active_roles(cls) -> List['Role']:
        """获取所有活跃角色"""
        try:
            return cls.filter_by(is_active=True).all()
        except:
            return []
    
    @classmethod
    def get_system_roles(cls) -> List['Role']:
        """获取所有系统角色"""
        try:
            return cls.filter_by(is_system=True).all()
        except:
            return []
    
    @classmethod
    def search_roles(cls, query: str, limit: int = 20) -> List['Role']:
        """搜索角色"""
        try:
            from sqlalchemy import or_
            
            search_filter = or_(
                cls.name.ilike(f'%{query}%'),
                cls.description.ilike(f'%{query}%')
            )
            
            return cls.filter_by().filter(search_filter).limit(limit).all()
        except:
            return []
    
    @classmethod
    def create_default_roles(cls):
        """创建默认系统角色"""
        default_roles = [
            {
                'name': 'admin',
                'description': '系统管理员，拥有所有权限',
                'is_system': True,
                'sort_order': "1"
            },
            {
                'name': 'manager',
                'description': '管理员，拥有大部分管理权限',
                'is_system': True,
                'sort_order': "2"
            },
            {
                'name': 'user',
                'description': '普通用户，拥有基本权限',
                'is_system': True,
                'sort_order': "3"
            },
            {
                'name': 'guest',
                'description': '访客用户，只有查看权限',
                'is_system': True,
                'sort_order': "4"
            }
        ]
        
        created_roles = []
        for role_data in default_roles:
            try:
                existing_role = cls.get_by_name(role_data['name'])
                if not existing_role:
                    role = cls.create_role(**role_data)
                    created_roles.append(role)
                    logger.info(f"创建默认角色: {role_data['name']}")
                else:
                    created_roles.append(existing_role)
            except Exception as e:
                logger.error(f"创建默认角色失败 {role_data['name']}: {e}")
        
        return created_roles
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, is_active={self.is_active})>"