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
    name = Column( String(100), unique=True, nullable=False, index=True, comment="权限名称")
    resource = Column( String(50), nullable=False, index=True, comment="资源名称")
    action = Column( String(50), nullable=False, index=True, comment="操作类型")
    description = Column( Text, nullable=True, comment="权限描述")
    
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
    
    # 业务逻辑方法已移至 PermissionService
    # 模型层只保留数据访问和基本验证方法
    
    def to_dict(self, exclude_fields: List[str] = None) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict(exclude_fields=exclude_fields)
        result['sort_order'] = int(self.sort_order or "0")
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
    
    # 权限创建逻辑已移至 PermissionService.create_permission()
    
    # 查询方法保留在模型层，但复杂业务逻辑移至服务层
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
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, resource={self.resource}, action={self.action})>"