"""
权限管理模块

定义权限类和权限检查逻辑
"""

from flask_principal import Permission as FlaskPermission, RoleNeed, UserNeed
from enum import Enum
from app.core.constants import UserRole
import logging

logger = logging.getLogger(__name__)


class PermissionType(Enum):
    """权限类型枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    USER_MANAGE = "user_manage"
    ROLE_MANAGE = "role_manage"
    SYSTEM_CONFIG = "system_config"


class Permission:
    """权限类"""
    
    def __init__(self, name, resource=None, action=None, description=None):
        self.name = name
        self.resource = resource or name
        self.action = action or "access"
        self.description = description or f"访问 {name}"
    
    def to_need(self):
        """转换为Flask-Principal需要的格式"""
        return RoleNeed(self.name)
    
    def __str__(self):
        return f"Permission({self.name})"
    
    def __repr__(self):
        return self.__str__()


class RolePermission:
    """角色权限管理类"""
    
    # 预定义权限
    PERMISSIONS = {
        'read': Permission('read', description='查看数据'),
        'write': Permission('write', description='编辑数据'),
        'delete': Permission('delete', description='删除数据'),
        'admin': Permission('admin', description='系统管理'),
        'user_manage': Permission('user_manage', description='用户管理'),
        'role_manage': Permission('role_manage', description='角色管理'),
        'system_config': Permission('system_config', description='系统配置'),
    }
    
    # 角色权限映射
    ROLE_PERMISSIONS = {
        UserRole.ADMIN.value: ['read', 'write', 'delete', 'admin', 'user_manage', 'role_manage', 'system_config'],
        UserRole.MANAGER.value: ['read', 'write', 'user_manage'],
        UserRole.USER.value: ['read'],
        UserRole.GUEST.value: [],
    }
    
    @classmethod
    def get_permission(cls, name):
        """获取权限对象"""
        return cls.PERMISSIONS.get(name)
    
    @classmethod
    def get_role_permissions(cls, role_name):
        """获取角色的所有权限"""
        permission_names = cls.ROLE_PERMISSIONS.get(role_name, [])
        return [cls.PERMISSIONS[name] for name in permission_names if name in cls.PERMISSIONS]
    
    @classmethod
    def has_permission(cls, user_roles, permission_name):
        """检查用户角色是否具有指定权限"""
        if not user_roles:
            return False
        
        for role in user_roles:
            role_name = role if isinstance(role, str) else role.name
            role_permissions = cls.ROLE_PERMISSIONS.get(role_name, [])
            if permission_name in role_permissions:
                return True
        
        return False
    
    @classmethod
    def create_flask_permission(cls, permission_name):
        """创建Flask-Principal权限对象"""
        return FlaskPermission(RoleNeed(permission_name))


# 预定义的权限实例
ReadPermission = RolePermission.create_flask_permission('read')
WritePermission = RolePermission.create_flask_permission('write')
DeletePermission = RolePermission.create_flask_permission('delete')
AdminPermission = RolePermission.create_flask_permission('admin')
UserManagePermission = RolePermission.create_flask_permission('user_manage')
RoleManagePermission = RolePermission.create_flask_permission('role_manage')
SystemConfigPermission = RolePermission.create_flask_permission('system_config')