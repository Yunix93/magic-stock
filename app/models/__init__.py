"""
数据模型模块

统一导入所有数据模型，确保正确的导入顺序
"""

# 首先导入基础模型
from app.models.base import BaseModel, Base

# 然后导入独立的模型（没有外键依赖）
from app.models.permission import Permission
from app.models.role import Role

# 再导入有外键依赖的模型
from app.models.logs import LoginLog, OperationLog
from app.models.user import User

# 最后导入关联表模型
from app.models.associations import UserRole, RolePermission

# 导出所有模型
__all__ = [
    'BaseModel',
    'Base',
    'User',
    'Role', 
    'Permission',
    'LoginLog',
    'OperationLog',
    'UserRole',
    'RolePermission'
]