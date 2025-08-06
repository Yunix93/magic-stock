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
    name = Column( String(50), unique=True, nullable=False, index=True, comment="角色名称")
    description = Column( Text, nullable=True, comment="角色描述")
    # 状态字段
    is_active = Column( Boolean, default=True, nullable=False, comment="是否激活")
    # 系统字段
    is_system = Column( Boolean, default=False, nullable=False, comment="是否为系统角色")
    # 排序字段
    sort_order = Column( String(10), default="0", nullable=False, comment="排序顺序")
    
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
    
    # 业务逻辑方法已移至 RoleService
    # 模型层只保留数据访问和基本验证方法
    
    def to_dict(self, exclude_fields: List[str] = None) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict(exclude_fields=exclude_fields)
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
    
    # 角色创建逻辑已移至 RoleService.create_role()
    
    # 查询方法保留在模型层，但复杂业务逻辑移至服务层
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Role']:
        """根据角色名称获取角色"""
        try:
            return cls.filter_by(name=name).first()
        except:
            return None
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, is_active={self.is_active})>"