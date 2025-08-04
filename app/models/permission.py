"""
权限数据模型

定义权限相关的数据模型和业务逻辑
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.core.validators import StringValidator
from app.core.constants import DatabaseTables
from app.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class Permission(BaseModel):
    """权限模型"""
    
    __tablename__ = DatabaseTables.PERMISSIONS
    
    # 基本信息字段
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="权限名称"
    )
    
    resource = Column(
        String(50),
        nullable=False,
        index=True,
        comment="资源名称"
    )
    
    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="操作类型"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="权限描述"
    )
    
    # 分组字段
    group = Column(
        String(50),
        nullable=True,
        index=True,
        comment="权限分组"
    )
    
    # 排序字段
    sort_order = Column(
        String(10),
        default="0",
        nullable=False,
        comment="排序顺序"
    )
    
    # 关系定义
    # roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    # 索引定义
    __table_args__ = (
        Index('idx_permission_name', 'name'),
        Index('idx_permission_resource', 'resource'),
        Index('idx_permission_action', 'action'),
        Index('idx_permission_group', 'group'),
        Index('idx_permission_resource_action', 'resource', 'action'),
    )
    
    def __init__(self, **kwargs):
        """初始化权限实例"""
        # 设置默认值
        kwargs.setdefault('sort_order', "0")
        
        # 验证必要字段
        if 'name' in kwargs:
            name_validator = StringValidator(min_length=2, max_length=100)
            kwargs['name'] = name_validator.validate(kwargs['name'], '权限名称')
        
        if 'resource' in kwargs:
            resource_validator = StringValidator(min_length=2, max_length=50)
            kwargs['resource'] = resource_validator.validate(kwargs['resource'], '资源名称')
        
        if 'action' in kwargs:
            action_validator = StringValidator(min_length=2, max_length=50)
            kwargs['action'] = action_validator.validate(kwargs['action'], '操作类型')
        
        # 自动生成权限名称（如果未提供）
        if 'name' not in kwargs and 'resource' in kwargs and 'action' in kwargs:
            kwargs['name'] = f"{kwargs['resource']}:{kwargs['action']}"
        
        super().__init__(**kwargs)
    
    def get_roles(self) -> List['Role']:
        """获取拥有此权限的所有角色"""
        from app.models.associations import RolePermission
        
        return RolePermission.get_roles_by_permission(self.id)
    
    def get_role_count(self) -> int:
        """获取拥有此权限的角色数量"""
        from app.models.associations import RolePermission
        
        return RolePermission.count_roles_by_permission(self.id)
    
    def get_users(self) -> List['User']:
        """获取通过角色拥有此权限的所有用户"""
        from app.models.associations import RolePermission, UserRole
        
        # 获取拥有此权限的角色
        roles = self.get_roles()
        
        # 获取这些角色的用户
        users = []
        for role in roles:
            role_users = UserRole.get_users_by_role(role.id)
            users.extend(role_users)
        
        # 去重
        unique_users = []
        seen_ids = set()
        for user in users:
            if user.id not in seen_ids:
                unique_users.append(user)
                seen_ids.add(user.id)
        
        return unique_users
    
    def can_be_deleted(self) -> bool:
        """检查权限是否可以被删除"""
        # 检查是否有角色使用此权限
        role_count = self.get_role_count()
        return role_count == 0
    
    def to_dict(self, exclude_fields: List[str] = None, include_roles: bool = False) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict(exclude_fields=exclude_fields)
        
        # 添加计算字段
        result['role_count'] = self.get_role_count()
        result['can_be_deleted'] = self.can_be_deleted()
        result['sort_order'] = int(self.sort_order or "0")
        
        # 包含角色信息
        if include_roles:
            roles = self.get_roles()
            result['roles'] = [r.to_dict() for r in roles]
        
        return result
    
    def to_public_dict(self) -> Dict[str, Any]:
        """转换为公开信息字典"""
        return {
            'id': self.id,
            'name': self.name,
            'resource': self.resource,
            'action': self.action,
            'description': self.description,
            'group': self.group,
            'sort_order': int(self.sort_order or "0"),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_permission(cls, name: str = None, resource: str = None, action: str = None, **kwargs) -> 'Permission':
        """创建新权限"""
        # 验证必要参数
        if not resource or not action:
            raise ValidationError("资源名称和操作类型不能为空")
        
        # 自动生成权限名称
        if not name:
            name = f"{resource}:{action}"
        
        # 验证权限名称唯一性
        if cls.get_by_name(name):
            raise ValidationError("权限名称已存在")
        
        # 创建权限实例
        permission = cls(
            name=name,
            resource=resource,
            action=action,
            **kwargs
        )
        
        # 保存到数据库
        permission.save()
        
        logger.info(f"新权限创建成功: {name}")
        return permission
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Permission']:
        """根据权限名称获取权限"""
        try:
            return cls.filter_by(name=name).first()
        except:
            return None
    
    @classmethod
    def get_by_resource_action(cls, resource: str, action: str) -> Optional['Permission']:
        """根据资源和操作获取权限"""
        try:
            return cls.filter_by(resource=resource, action=action).first()
        except:
            return None
    
    @classmethod
    def get_by_resource(cls, resource: str) -> List['Permission']:
        """获取指定资源的所有权限"""
        try:
            return cls.filter_by(resource=resource).all()
        except:
            return []
    
    @classmethod
    def get_by_group(cls, group: str) -> List['Permission']:
        """获取指定分组的所有权限"""
        try:
            return cls.filter_by(group=group).all()
        except:
            return []
    
    @classmethod
    def get_all_resources(cls) -> List[str]:
        """获取所有资源名称"""
        try:
            from sqlalchemy import distinct
            from app.models.base import db_session
            
            if not db_session:
                return []
            
            result = db_session.query(distinct(cls.resource)).all()
            return [r[0] for r in result if r[0]]
        except:
            return []
    
    @classmethod
    def get_all_actions(cls) -> List[str]:
        """获取所有操作类型"""
        try:
            from sqlalchemy import distinct
            from app.models.base import db_session
            
            if not db_session:
                return []
            
            result = db_session.query(distinct(cls.action)).all()
            return [a[0] for a in result if a[0]]
        except:
            return []
    
    @classmethod
    def get_all_groups(cls) -> List[str]:
        """获取所有权限分组"""
        try:
            from sqlalchemy import distinct
            from app.models.base import db_session
            
            if not db_session:
                return []
            
            result = db_session.query(distinct(cls.group)).filter(cls.group.isnot(None)).all()
            return [g[0] for g in result if g[0]]
        except:
            return []
    
    @classmethod
    def get_all(cls) -> List['Permission']:
        """获取所有权限"""
        try:
            return cls.filter_by().all()
        except Exception as e:
            logger.error(f"获取所有权限失败: {e}")
            return []
    
    @classmethod
    def search_permissions(cls, query: str, limit: int = 20) -> List['Permission']:
        """搜索权限"""
        try:
            from sqlalchemy import or_
            
            search_filter = or_(
                cls.name.ilike(f'%{query}%'),
                cls.resource.ilike(f'%{query}%'),
                cls.action.ilike(f'%{query}%'),
                cls.description.ilike(f'%{query}%')
            )
            
            return cls.filter_by().filter(search_filter).limit(limit).all()
        except:
            return []
    
    @classmethod
    def create_default_permissions(cls):
        """创建默认系统权限"""
        default_permissions = [
            # 用户管理权限
            {'resource': 'user', 'action': 'create', 'description': '创建用户', 'group': '用户管理'},
            {'resource': 'user', 'action': 'read', 'description': '查看用户', 'group': '用户管理'},
            {'resource': 'user', 'action': 'update', 'description': '更新用户', 'group': '用户管理'},
            {'resource': 'user', 'action': 'delete', 'description': '删除用户', 'group': '用户管理'},
            {'resource': 'user', 'action': 'list', 'description': '用户列表', 'group': '用户管理'},
            
            # 角色管理权限
            {'resource': 'role', 'action': 'create', 'description': '创建角色', 'group': '角色管理'},
            {'resource': 'role', 'action': 'read', 'description': '查看角色', 'group': '角色管理'},
            {'resource': 'role', 'action': 'update', 'description': '更新角色', 'group': '角色管理'},
            {'resource': 'role', 'action': 'delete', 'description': '删除角色', 'group': '角色管理'},
            {'resource': 'role', 'action': 'list', 'description': '角色列表', 'group': '角色管理'},
            
            # 权限管理权限
            {'resource': 'permission', 'action': 'create', 'description': '创建权限', 'group': '权限管理'},
            {'resource': 'permission', 'action': 'read', 'description': '查看权限', 'group': '权限管理'},
            {'resource': 'permission', 'action': 'update', 'description': '更新权限', 'group': '权限管理'},
            {'resource': 'permission', 'action': 'delete', 'description': '删除权限', 'group': '权限管理'},
            {'resource': 'permission', 'action': 'list', 'description': '权限列表', 'group': '权限管理'},
            
            # 系统管理权限
            {'resource': 'system', 'action': 'config', 'description': '系统配置', 'group': '系统管理'},
            {'resource': 'system', 'action': 'monitor', 'description': '系统监控', 'group': '系统管理'},
            {'resource': 'system', 'action': 'log', 'description': '系统日志', 'group': '系统管理'},
            {'resource': 'system', 'action': 'backup', 'description': '数据备份', 'group': '系统管理'},
            
            # 仪表板权限
            {'resource': 'dashboard', 'action': 'view', 'description': '查看仪表板', 'group': '仪表板'},
            {'resource': 'dashboard', 'action': 'export', 'description': '导出数据', 'group': '仪表板'},
        ]
        
        created_permissions = []
        for perm_data in default_permissions:
            try:
                name = f"{perm_data['resource']}:{perm_data['action']}"
                existing_permission = cls.get_by_name(name)
                if not existing_permission:
                    permission = cls.create_permission(**perm_data)
                    created_permissions.append(permission)
                    logger.info(f"创建默认权限: {name}")
                else:
                    created_permissions.append(existing_permission)
            except Exception as e:
                logger.error(f"创建默认权限失败 {perm_data}: {e}")
        
        return created_permissions
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, resource={self.resource}, action={self.action})>"