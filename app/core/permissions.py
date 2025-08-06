"""
权限管理模块

定义现代化的权限类和权限检查逻辑
"""

from typing import Dict, List, Set, Optional, Union
from enum import Enum
from dataclasses import dataclass
from app.core.constants import UserStatus
import logging

logger = logging.getLogger(__name__)


class PermissionAction(Enum):
    """权限操作类型枚举"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    EXPORT = "export"
    IMPORT = "import"
    MANAGE = "manage"
    CONFIG = "config"
    MONITOR = "monitor"
    BACKUP = "backup"
    RESTORE = "restore"


class ResourceType(Enum):
    """资源类型枚举"""
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    SYSTEM = "system"
    DASHBOARD = "dashboard"
    LOG = "log"
    CONFIG = "config"
    BACKUP = "backup"
    MONITOR = "monitor"


@dataclass
class PermissionDefinition:
    """权限定义数据类"""
    name: str
    resource: str
    action: str
    description: str
    group: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.name:
            self.name = f"{self.resource}:{self.action}"
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, PermissionDefinition):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return False


class PermissionRegistry:
    """权限注册表"""
    
    def __init__(self):
        self._permissions: Dict[str, PermissionDefinition] = {}
        self._groups: Dict[str, List[PermissionDefinition]] = {}
        self._initialize_default_permissions()
    
    def _initialize_default_permissions(self):
        """初始化默认权限"""
        default_permissions = [
            # 用户管理权限
            PermissionDefinition("user:create", "user", "create", "创建用户", "用户管理"),
            PermissionDefinition("user:read", "user", "read", "查看用户", "用户管理"),
            PermissionDefinition("user:update", "user", "update", "更新用户", "用户管理"),
            PermissionDefinition("user:delete", "user", "delete", "删除用户", "用户管理"),
            PermissionDefinition("user:list", "user", "list", "用户列表", "用户管理"),
            PermissionDefinition("user:export", "user", "export", "导出用户", "用户管理"),
            
            # 角色管理权限
            PermissionDefinition("role:create", "role", "create", "创建角色", "角色管理"),
            PermissionDefinition("role:read", "role", "read", "查看角色", "角色管理"),
            PermissionDefinition("role:update", "role", "update", "更新角色", "角色管理"),
            PermissionDefinition("role:delete", "role", "delete", "删除角色", "角色管理"),
            PermissionDefinition("role:list", "role", "list", "角色列表", "角色管理"),
            
            # 权限管理权限
            PermissionDefinition("permission:create", "permission", "create", "创建权限", "权限管理"),
            PermissionDefinition("permission:read", "permission", "read", "查看权限", "权限管理"),
            PermissionDefinition("permission:update", "permission", "update", "更新权限", "权限管理"),
            PermissionDefinition("permission:delete", "permission", "delete", "删除权限", "权限管理"),
            PermissionDefinition("permission:list", "permission", "list", "权限列表", "权限管理"),
            
            # 系统管理权限
            PermissionDefinition("system:config", "system", "config", "系统配置", "系统管理"),
            PermissionDefinition("system:monitor", "system", "monitor", "系统监控", "系统管理"),
            PermissionDefinition("system:backup", "system", "backup", "数据备份", "系统管理"),
            PermissionDefinition("system:restore", "system", "restore", "数据恢复", "系统管理"),
            
            # 仪表板权限
            PermissionDefinition("dashboard:view", "dashboard", "view", "查看仪表板", "仪表板"),
            PermissionDefinition("dashboard:export", "dashboard", "export", "导出数据", "仪表板"),
            
            # 日志管理权限
            PermissionDefinition("log:read", "log", "read", "查看日志", "日志管理"),
            PermissionDefinition("log:export", "log", "export", "导出日志", "日志管理"),
            PermissionDefinition("log:delete", "log", "delete", "删除日志", "日志管理"),
        ]
        
        for perm in default_permissions:
            self.register(perm)
    
    def register(self, permission: PermissionDefinition):
        """注册权限"""
        self._permissions[permission.name] = permission
        
        # 按组分类
        if permission.group:
            if permission.group not in self._groups:
                self._groups[permission.group] = []
            self._groups[permission.group].append(permission)
        
        logger.debug(f"注册权限: {permission.name}")
    
    def get(self, name: str) -> Optional[PermissionDefinition]:
        """获取权限"""
        return self._permissions.get(name)
    
    def get_all(self) -> List[PermissionDefinition]:
        """获取所有权限"""
        return list(self._permissions.values())
    
    def get_by_group(self, group: str) -> List[PermissionDefinition]:
        """按组获取权限"""
        return self._groups.get(group, [])
    
    def get_groups(self) -> List[str]:
        """获取所有权限组"""
        return list(self._groups.keys())
    
    def get_by_resource(self, resource: str) -> List[PermissionDefinition]:
        """按资源获取权限"""
        return [perm for perm in self._permissions.values() if perm.resource == resource]
    
    def exists(self, name: str) -> bool:
        """检查权限是否存在"""
        return name in self._permissions


class RolePermissionManager:
    """角色权限管理器"""
    
    def __init__(self, permission_registry: PermissionRegistry):
        self.registry = permission_registry
        self._role_permissions: Dict[str, Set[str]] = {}
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """初始化默认角色权限"""
        default_role_permissions = {
            'admin': [
                # 管理员拥有所有权限
                'user:create', 'user:read', 'user:update', 'user:delete', 'user:list', 'user:export',
                'role:create', 'role:read', 'role:update', 'role:delete', 'role:list',
                'permission:create', 'permission:read', 'permission:update', 'permission:delete', 'permission:list',
                'system:config', 'system:monitor', 'system:backup', 'system:restore',
                'dashboard:view', 'dashboard:export',
                'log:read', 'log:export', 'log:delete',
            ],
            'manager': [
                # 管理员拥有用户管理和查看权限
                'user:read', 'user:update', 'user:list', 'user:export',
                'role:read', 'role:list',
                'permission:read', 'permission:list',
                'dashboard:view', 'dashboard:export',
                'log:read', 'log:export',
            ],
            'user': [
                # 普通用户只有查看权限
                'dashboard:view',
                'user:read',  # 只能查看自己的信息
            ],
            'guest': [
                # 访客只有基本查看权限
                'dashboard:view',
            ]
        }
        
        for role_name, permissions in default_role_permissions.items():
            self._role_permissions[role_name] = set(permissions)
    
    def assign_permission_to_role(self, role_name: str, permission_name: str):
        """为角色分配权限"""
        if not self.registry.exists(permission_name):
            raise ValueError(f"权限不存在: {permission_name}")
        
        if role_name not in self._role_permissions:
            self._role_permissions[role_name] = set()
        
        self._role_permissions[role_name].add(permission_name)
        logger.info(f"为角色 {role_name} 分配权限: {permission_name}")
    
    def revoke_permission_from_role(self, role_name: str, permission_name: str):
        """从角色撤销权限"""
        if role_name in self._role_permissions:
            self._role_permissions[role_name].discard(permission_name)
            logger.info(f"从角色 {role_name} 撤销权限: {permission_name}")
    
    def get_role_permissions(self, role_name: str) -> Set[str]:
        """获取角色的所有权限"""
        return self._role_permissions.get(role_name, set()).copy()
    
    def has_permission(self, role_names: Union[str, List[str]], permission_name: str) -> bool:
        """检查角色是否具有指定权限"""
        if isinstance(role_names, str):
            role_names = [role_names]
        
        for role_name in role_names:
            if permission_name in self._role_permissions.get(role_name, set()):
                return True
        
        return False
    
    def get_user_permissions(self, user_roles: List[str]) -> Set[str]:
        """获取用户通过角色拥有的所有权限"""
        permissions = set()
        for role_name in user_roles:
            permissions.update(self._role_permissions.get(role_name, set()))
        return permissions


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, permission_registry: PermissionRegistry, role_manager: RolePermissionManager):
        self.registry = permission_registry
        self.role_manager = role_manager
    
    def check_permission(self, user, permission_name: str) -> bool:
        """检查用户权限"""
        if not user:
            return False
        
        # 超级用户拥有所有权限
        if getattr(user, 'is_superuser', False):
            return True
        
        # 检查用户是否激活
        if not getattr(user, 'is_active', True):
            return False
        
        # 获取用户角色
        user_roles = []
        from app.services.user_service import user_service
        try:
            # 通过服务层获取用户角色
            roles = user_service.get_user_roles(user.id)
            user_roles = [role.name for role in roles]
        except:
            # 如果服务层调用失败，尝试直接访问关系属性
            if hasattr(user, 'roles'):
                user_roles = [role.name for role in user.roles]
        
        # 检查角色权限
        return self.role_manager.has_permission(user_roles, permission_name)
    
    def check_role(self, user, role_name: str) -> bool:
        """检查用户角色"""
        if not user:
            return False
        
        # 通过服务层检查用户角色
        from app.services.user_service import user_service
        try:
            return user_service.check_user_role(user.id, role_name)
        except:
            # 如果服务层调用失败，尝试直接访问关系属性
            if hasattr(user, 'roles'):
                return any(role.name == role_name for role in user.roles)
            return False
    
    def get_user_permissions(self, user) -> Set[str]:
        """获取用户的所有权限"""
        if not user:
            return set()
        
        # 超级用户拥有所有权限
        if getattr(user, 'is_superuser', False):
            return set(self.registry._permissions.keys())
        
        # 获取用户角色
        user_roles = []
        from app.services.user_service import user_service
        try:
            # 通过服务层获取用户角色
            roles = user_service.get_user_roles(user.id)
            user_roles = [role.name for role in roles]
        except:
            # 如果服务层调用失败，尝试直接访问关系属性
            if hasattr(user, 'roles'):
                user_roles = [role.name for role in user.roles]
        
        return self.role_manager.get_user_permissions(user_roles)


# 全局权限管理实例
permission_registry = PermissionRegistry()
role_permission_manager = RolePermissionManager(permission_registry)
permission_checker = PermissionChecker(permission_registry, role_permission_manager)


def has_permission(user, permission_name: str) -> bool:
    """全局权限检查函数"""
    return permission_checker.check_permission(user, permission_name)


def has_role(user, role_name: str) -> bool:
    """全局角色检查函数"""
    return permission_checker.check_role(user, role_name)


def get_user_permissions(user) -> Set[str]:
    """获取用户权限列表"""
    return permission_checker.get_user_permissions(user)