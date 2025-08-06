"""
角色权限服务层

提供角色和权限管理的业务逻辑和数据操作服务
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.core.extensions import get_db_session
from app.core.validators import StringValidator
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError
from app.core.constants import UserRole
import logging

logger = logging.getLogger(__name__)


class RoleService:
    """角色服务类 - 提供角色管理的业务逻辑"""
    
    def __init__(self, session: Optional[Session] = None):
        """
        初始化角色服务
        
        Args:
            session: 可选的数据库会话，如果不提供则自动创建
        """
        self.session = session
    
    def _get_session(self) -> Session:
        """获取数据库会话"""
        if self.session:
            return self.session
        return get_db_session()
    
    # ============================================================================
    # 角色创建和管理
    # ============================================================================
    
    def create_role(self, role_data: Dict[str, Any], created_by: Optional[str] = None) -> Role:
        """
        创建新角色
        
        Args:
            role_data: 角色数据字典
            created_by: 创建者用户ID
            
        Returns:
            Role: 创建的角色对象
        """
        try:
            # 验证角色数据
            validated_data = self._validate_role_creation_data(role_data)
            
            # 检查角色名称唯一性
            self._check_role_name_uniqueness(validated_data['name'])
            
            # 创建角色对象
            role = Role(
                name=validated_data['name'],
                description=validated_data.get('description', ''),
                is_active=validated_data.get('is_active', True),
                is_system=validated_data.get('is_system', False),
                sort_order=validated_data.get('sort_order', "0")
            )
            
            with get_db_session() as session:
                session.add(role)
                session.commit()
                session.refresh(role)
                
                # 记录操作日志
                if created_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=created_by,
                        operation='create_role',
                        resource='role',
                        details={
                            'role_id': role.id,
                            'role_name': role.name,
                            'description': role.description
                        }
                    )
                
                logger.info(f"角色创建成功: {role.name} (ID: {role.id})")
                return role
                
        except IntegrityError as e:
            logger.error(f"角色创建失败 - 数据完整性错误: {e}")
            raise BusinessLogicError("角色名称已存在")
        except Exception as e:
            logger.error(f"角色创建失败: {e}")
            raise DatabaseError(f"角色创建失败: {str(e)}")
    
    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """
        根据ID获取角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            Optional[Role]: 角色对象或None
        """
        try:
            with get_db_session() as session:
                return session.query(Role).filter(Role.id == role_id).first()
        except Exception as e:
            logger.error(f"获取角色失败 (ID: {role_id}): {e}")
            return None
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """
        根据名称获取角色
        
        Args:
            name: 角色名称
            
        Returns:
            Optional[Role]: 角色对象或None
        """
        try:
            with get_db_session() as session:
                return session.query(Role).filter(Role.name == name).first()
        except Exception as e:
            logger.error(f"获取角色失败 (名称: {name}): {e}")
            return None
    
    def get_roles_list(self, 
                      page: int = 1, 
                      per_page: int = 20,
                      search: Optional[str] = None,
                      is_active: Optional[bool] = None,
                      is_system: Optional[bool] = None,
                      sort_by: str = 'created_at',
                      sort_order: str = 'desc') -> Tuple[List[Role], int]:
        """
        获取角色列表（分页）
        
        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词
            is_active: 是否激活筛选
            is_system: 是否系统角色筛选
            sort_by: 排序字段
            sort_order: 排序方向
            
        Returns:
            Tuple[List[Role], int]: (角色列表, 总数量)
        """
        try:
            with get_db_session() as session:
                query = session.query(Role)
                
                # 搜索条件
                if search:
                    search_filter = or_(
                        Role.name.ilike(f'%{search}%'),
                        Role.description.ilike(f'%{search}%')
                    )
                    query = query.filter(search_filter)
                
                # 状态筛选
                if is_active is not None:
                    query = query.filter(Role.is_active == is_active)
                
                # 系统角色筛选
                if is_system is not None:
                    query = query.filter(Role.is_system == is_system)
                
                # 排序
                if hasattr(Role, sort_by):
                    order_column = getattr(Role, sort_by)
                    if sort_order.lower() == 'desc':
                        query = query.order_by(order_column.desc())
                    else:
                        query = query.order_by(order_column.asc())
                
                # 获取总数
                total = query.count()
                
                # 分页
                offset = (page - 1) * per_page
                roles = query.offset(offset).limit(per_page).all()
                
                return roles, total
                
        except Exception as e:
            logger.error(f"获取角色列表失败: {e}")
            raise DatabaseError(f"获取角色列表失败: {str(e)}")
    
    def update_role(self, role_id: str, update_data: Dict[str, Any], 
                   updated_by: Optional[str] = None) -> Role:
        """
        更新角色信息
        
        Args:
            role_id: 角色ID
            update_data: 更新数据
            updated_by: 更新者用户ID
            
        Returns:
            Role: 更新后的角色对象
        """
        try:
            # 验证更新数据
            validated_data = self._validate_role_update_data(update_data)
            
            with get_db_session() as session:
                role = session.query(Role).filter(Role.id == role_id).first()
                if not role:
                    raise BusinessLogicError(f"角色不存在: {role_id}")
                
                # 检查系统角色保护
                if role.is_system and 'name' in validated_data:
                    raise BusinessLogicError("系统角色名称不能修改")
                
                # 检查名称唯一性（排除当前角色）
                if 'name' in validated_data:
                    self._check_role_name_uniqueness(
                        validated_data['name'],
                        exclude_role_id=role_id
                    )
                
                # 记录更新前的数据
                old_data = {
                    'name': role.name,
                    'description': role.description,
                    'is_active': role.is_active
                }
                
                # 更新角色信息
                for field, value in validated_data.items():
                    if hasattr(role, field):
                        setattr(role, field, value)
                
                role.updated_at = datetime.now(timezone.utc)
                role.updated_by = updated_by
                
                session.commit()
                session.refresh(role)
                
                # 记录操作日志
                if updated_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=updated_by,
                        operation='update_role',
                        resource='role',
                        details={
                            'role_id': role.id,
                            'old_data': old_data,
                            'new_data': validated_data
                        }
                    )
                
                logger.info(f"角色更新成功: {role.name} (ID: {role.id})")
                return role
                
        except IntegrityError as e:
            logger.error(f"角色更新失败 - 数据完整性错误: {e}")
            raise BusinessLogicError("角色名称已存在")
        except Exception as e:
            logger.error(f"角色更新失败: {e}")
            raise DatabaseError(f"角色更新失败: {str(e)}")
    
    def delete_role(self, role_id: str, deleted_by: Optional[str] = None,
                   soft_delete: bool = True) -> bool:
        """
        删除角色
        
        Args:
            role_id: 角色ID
            deleted_by: 操作者用户ID
            soft_delete: 是否软删除
            
        Returns:
            bool: 是否删除成功
        """
        try:
            with get_db_session() as session:
                role = session.query(Role).filter(Role.id == role_id).first()
                if not role:
                    raise BusinessLogicError(f"角色不存在: {role_id}")
                
                # 检查系统角色保护
                if role.is_system:
                    raise BusinessLogicError("系统角色不能被删除")
                
                # 检查是否有用户使用该角色
                user_count = session.query(User).join(User.roles).filter(
                    Role.id == role_id
                ).count()
                
                if user_count > 0:
                    raise BusinessLogicError(f"角色 {role.name} 正在被 {user_count} 个用户使用，无法删除")
                
                if soft_delete:
                    # 软删除
                    role.is_deleted = True
                    role.deleted_at = datetime.now(timezone.utc)
                    role.deleted_by = deleted_by
                    session.commit()
                else:
                    # 硬删除
                    session.delete(role)
                    session.commit()
                
                # 记录操作日志
                if deleted_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=deleted_by,
                        operation='delete_role',
                        resource='role',
                        details={
                            'role_id': role_id,
                            'role_name': role.name,
                            'soft_delete': soft_delete
                        }
                    )
                
                logger.info(f"角色删除成功: {role.name} (软删除: {soft_delete})")
                return True
                
        except Exception as e:
            logger.error(f"角色删除失败: {e}")
            raise DatabaseError(f"角色删除失败: {str(e)}")
    
    # ============================================================================
    # 权限管理
    # ============================================================================
    
    def create_permission(self, permission_data: Dict[str, Any], 
                         created_by: Optional[str] = None) -> Permission:
        """
        创建新权限
        
        Args:
            permission_data: 权限数据字典
            created_by: 创建者用户ID
            
        Returns:
            Permission: 创建的权限对象
        """
        try:
            # 验证权限数据
            validated_data = self._validate_permission_creation_data(permission_data)
            
            # 检查权限名称唯一性
            self._check_permission_name_uniqueness(validated_data['name'])
            
            # 创建权限对象
            permission = Permission(
                name=validated_data['name'],
                resource=validated_data['resource'],
                action=validated_data['action'],
                description=validated_data.get('description', ''),
                group=validated_data.get('group'),
                sort_order=validated_data.get('sort_order', "0"),
                created_by=created_by
            )
            
            with get_db_session() as session:
                session.add(permission)
                session.commit()
                session.refresh(permission)
                
                # 记录操作日志
                if created_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=created_by,
                        operation='create_permission',
                        resource='permission',
                        details={
                            'permission_id': permission.id,
                            'permission_name': permission.name,
                            'resource': permission.resource,
                            'action': permission.action
                        }
                    )
                
                logger.info(f"权限创建成功: {permission.name} (ID: {permission.id})")
                return permission
                
        except IntegrityError as e:
            logger.error(f"权限创建失败 - 数据完整性错误: {e}")
            raise BusinessLogicError("权限名称已存在")
        except Exception as e:
            logger.error(f"权限创建失败: {e}")
            raise DatabaseError(f"权限创建失败: {str(e)}")
    
    def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """
        根据ID获取权限
        
        Args:
            permission_id: 权限ID
            
        Returns:
            Optional[Permission]: 权限对象或None
        """
        try:
            with get_db_session() as session:
                return session.query(Permission).filter(Permission.id == permission_id).first()
        except Exception as e:
            logger.error(f"获取权限失败 (ID: {permission_id}): {e}")
            return None
    
    def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """
        根据名称获取权限
        
        Args:
            name: 权限名称
            
        Returns:
            Optional[Permission]: 权限对象或None
        """
        try:
            with get_db_session() as session:
                return session.query(Permission).filter(Permission.name == name).first()
        except Exception as e:
            logger.error(f"获取权限失败 (名称: {name}): {e}")
            return None
    
    def get_permissions_list(self, 
                           page: int = 1, 
                           per_page: int = 20,
                           search: Optional[str] = None,
                           resource: Optional[str] = None,
                           group: Optional[str] = None,
                           sort_by: str = 'created_at',
                           sort_order: str = 'desc') -> Tuple[List[Permission], int]:
        """
        获取权限列表（分页）
        
        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词
            resource: 资源筛选
            group: 分组筛选
            sort_by: 排序字段
            sort_order: 排序方向
            
        Returns:
            Tuple[List[Permission], int]: (权限列表, 总数量)
        """
        try:
            with get_db_session() as session:
                query = session.query(Permission)
                
                # 搜索条件
                if search:
                    search_filter = or_(
                        Permission.name.ilike(f'%{search}%'),
                        Permission.description.ilike(f'%{search}%'),
                        Permission.resource.ilike(f'%{search}%'),
                        Permission.action.ilike(f'%{search}%')
                    )
                    query = query.filter(search_filter)
                
                # 资源筛选
                if resource:
                    query = query.filter(Permission.resource == resource)
                
                # 分组筛选
                if group:
                    query = query.filter(Permission.group == group)
                
                # 排序
                if hasattr(Permission, sort_by):
                    order_column = getattr(Permission, sort_by)
                    if sort_order.lower() == 'desc':
                        query = query.order_by(order_column.desc())
                    else:
                        query = query.order_by(order_column.asc())
                
                # 获取总数
                total = query.count()
                
                # 分页
                offset = (page - 1) * per_page
                permissions = query.offset(offset).limit(per_page).all()
                
                return permissions, total
                
        except Exception as e:
            logger.error(f"获取权限列表失败: {e}")
            raise DatabaseError(f"获取权限列表失败: {str(e)}") 
   
    # ============================================================================
    # 角色权限分配和回收
    # ============================================================================
    
    def assign_permission_to_role(self, role_id: str, permission_id: str,
                                 assigned_by: Optional[str] = None) -> bool:
        """
        为角色分配权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
            assigned_by: 操作者用户ID
            
        Returns:
            bool: 是否分配成功
        """
        try:
            with get_db_session() as session:
                role = session.query(Role).filter(Role.id == role_id).first()
                permission = session.query(Permission).filter(Permission.id == permission_id).first()
                
                if not role:
                    raise BusinessLogicError(f"角色不存在: {role_id}")
                if not permission:
                    raise BusinessLogicError(f"权限不存在: {permission_id}")
                
                # 检查权限是否已经分配
                if self._role_has_permission(role_id, permission_id, session):
                    logger.warning(f"角色 {role.name} 已经拥有权限 {permission.name}")
                    return True
                
                # 创建角色权限关联
                self._create_role_permission_association(role_id, permission_id, session)
                
                session.commit()
                
                # 记录操作日志
                if assigned_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=assigned_by,
                        operation='assign_permission_to_role',
                        resource='role',
                        details={
                            'role_id': role_id,
                            'role_name': role.name,
                            'permission_id': permission_id,
                            'permission_name': permission.name
                        }
                    )
                
                logger.info(f"权限分配成功: 角色 {role.name} 获得权限 {permission.name}")
                return True
                
        except Exception as e:
            logger.error(f"权限分配失败: {e}")
            raise DatabaseError(f"权限分配失败: {str(e)}")
    
    def revoke_permission_from_role(self, role_id: str, permission_id: str,
                                   revoked_by: Optional[str] = None) -> bool:
        """
        从角色回收权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
            revoked_by: 操作者用户ID
            
        Returns:
            bool: 是否回收成功
        """
        try:
            with get_db_session() as session:
                role = session.query(Role).filter(Role.id == role_id).first()
                permission = session.query(Permission).filter(Permission.id == permission_id).first()
                
                if not role:
                    raise BusinessLogicError(f"角色不存在: {role_id}")
                if not permission:
                    raise BusinessLogicError(f"权限不存在: {permission_id}")
                
                # 检查权限是否存在
                if not self._role_has_permission(role_id, permission_id, session):
                    logger.warning(f"角色 {role.name} 不拥有权限 {permission.name}")
                    return True
                
                # 删除角色权限关联
                self._delete_role_permission_association(role_id, permission_id, session)
                
                session.commit()
                
                # 记录操作日志
                if revoked_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=revoked_by,
                        operation='revoke_permission_from_role',
                        resource='role',
                        details={
                            'role_id': role_id,
                            'role_name': role.name,
                            'permission_id': permission_id,
                            'permission_name': permission.name
                        }
                    )
                
                logger.info(f"权限回收成功: 角色 {role.name} 失去权限 {permission.name}")
                return True
                
        except Exception as e:
            logger.error(f"权限回收失败: {e}")
            raise DatabaseError(f"权限回收失败: {str(e)}")
    
    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """
        获取角色的所有权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            List[Permission]: 权限列表
        """
        try:
            with get_db_session() as session:
                # 通过关联表查询角色权限
                permissions = session.query(Permission).join(
                    self._get_role_permission_table()
                ).filter(
                    self._get_role_permission_table().c.role_id == role_id
                ).all()
                
                return permissions
                
        except Exception as e:
            logger.error(f"获取角色权限失败: {e}")
            return []
    
    def get_permission_roles(self, permission_id: str) -> List[Role]:
        """
        获取拥有指定权限的所有角色
        
        Args:
            permission_id: 权限ID
            
        Returns:
            List[Role]: 角色列表
        """
        try:
            with get_db_session() as session:
                # 通过关联表查询权限角色
                roles = session.query(Role).join(
                    self._get_role_permission_table()
                ).filter(
                    self._get_role_permission_table().c.permission_id == permission_id
                ).all()
                
                return roles
                
        except Exception as e:
            logger.error(f"获取权限角色失败: {e}")
            return []
    
    def batch_assign_permissions_to_role(self, role_id: str, permission_ids: List[str],
                                        assigned_by: Optional[str] = None) -> Dict[str, Any]:
        """
        批量为角色分配权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            assigned_by: 操作者用户ID
            
        Returns:
            Dict[str, Any]: 分配结果统计
        """
        try:
            with get_db_session() as session:
                role = session.query(Role).filter(Role.id == role_id).first()
                if not role:
                    raise BusinessLogicError(f"角色不存在: {role_id}")
                
                success_count = 0
                failed_count = 0
                already_exists_count = 0
                failed_permissions = []
                
                for permission_id in permission_ids:
                    try:
                        permission = session.query(Permission).filter(
                            Permission.id == permission_id
                        ).first()
                        
                        if not permission:
                            failed_count += 1
                            failed_permissions.append(permission_id)
                            continue
                        
                        # 检查权限是否已经分配
                        if self._role_has_permission(role_id, permission_id, session):
                            already_exists_count += 1
                            continue
                        
                        # 创建角色权限关联
                        self._create_role_permission_association(role_id, permission_id, session)
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"分配权限失败 {permission_id}: {e}")
                        failed_count += 1
                        failed_permissions.append(permission_id)
                
                session.commit()
                
                # 记录操作日志
                if assigned_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=assigned_by,
                        operation='batch_assign_permissions_to_role',
                        resource='role',
                        details={
                            'role_id': role_id,
                            'role_name': role.name,
                            'permission_count': len(permission_ids),
                            'success_count': success_count,
                            'failed_count': failed_count,
                            'already_exists_count': already_exists_count
                        }
                    )
                
                result = {
                    'total': len(permission_ids),
                    'success': success_count,
                    'failed': failed_count,
                    'already_exists': already_exists_count,
                    'failed_permissions': failed_permissions
                }
                
                logger.info(f"批量权限分配完成: 角色 {role.name}, 结果: {result}")
                return result
                
        except Exception as e:
            logger.error(f"批量权限分配失败: {e}")
            raise DatabaseError(f"批量权限分配失败: {str(e)}")
    
    def batch_revoke_permissions_from_role(self, role_id: str, permission_ids: List[str],
                                          revoked_by: Optional[str] = None) -> Dict[str, Any]:
        """
        批量从角色回收权限
        
        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
            revoked_by: 操作者用户ID
            
        Returns:
            Dict[str, Any]: 回收结果统计
        """
        try:
            with get_db_session() as session:
                role = session.query(Role).filter(Role.id == role_id).first()
                if not role:
                    raise BusinessLogicError(f"角色不存在: {role_id}")
                
                success_count = 0
                failed_count = 0
                not_exists_count = 0
                failed_permissions = []
                
                for permission_id in permission_ids:
                    try:
                        permission = session.query(Permission).filter(
                            Permission.id == permission_id
                        ).first()
                        
                        if not permission:
                            failed_count += 1
                            failed_permissions.append(permission_id)
                            continue
                        
                        # 检查权限是否存在
                        if not self._role_has_permission(role_id, permission_id, session):
                            not_exists_count += 1
                            continue
                        
                        # 删除角色权限关联
                        self._delete_role_permission_association(role_id, permission_id, session)
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"回收权限失败 {permission_id}: {e}")
                        failed_count += 1
                        failed_permissions.append(permission_id)
                
                session.commit()
                
                # 记录操作日志
                if revoked_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=revoked_by,
                        operation='batch_revoke_permissions_from_role',
                        resource='role',
                        details={
                            'role_id': role_id,
                            'role_name': role.name,
                            'permission_count': len(permission_ids),
                            'success_count': success_count,
                            'failed_count': failed_count,
                            'not_exists_count': not_exists_count
                        }
                    )
                
                result = {
                    'total': len(permission_ids),
                    'success': success_count,
                    'failed': failed_count,
                    'not_exists': not_exists_count,
                    'failed_permissions': failed_permissions
                }
                
                logger.info(f"批量权限回收完成: 角色 {role.name}, 结果: {result}")
                return result
                
        except Exception as e:
            logger.error(f"批量权限回收失败: {e}")
            raise DatabaseError(f"批量权限回收失败: {str(e)}")
    
    # ============================================================================
    # 注意：用户权限检查方法已移至 UserService
    # RoleService 专注于角色和权限的管理，不处理用户相关逻辑
    # ============================================================================
                
            return {
                    'is_superuser': False,
                    'roles': roles_data,
                    'permissions': list(all_permissions),
                    'total_permissions': len(all_permissions)
                }
                
        except Exception as e:
            logger.error(f"获取用户角色权限详情失败: {e}")
            return {'roles': [], 'permissions': [], 'total_permissions': 0}
    
    # ============================================================================
    # 统计和分析
    # ============================================================================
    
    def get_role_statistics(self) -> Dict[str, Any]:
        """
        获取角色统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            with get_db_session() as session:
                # 总角色数
                total_roles = session.query(Role).count()
                
                # 活跃角色数
                active_roles = session.query(Role).filter(Role.is_active == True).count()
                
                # 系统角色数
                system_roles = session.query(Role).filter(Role.is_system == True).count()
                
                # 自定义角色数
                custom_roles = total_roles - system_roles
                
                # 权限统计
                total_permissions = session.query(Permission).count()
                
                # 角色权限分布
                role_permission_counts = session.query(
                    Role.name,
                    func.count(self._get_role_permission_table().c.permission_id).label('permission_count')
                ).outerjoin(
                    self._get_role_permission_table()
                ).group_by(Role.id, Role.name).all()
                
                return {
                    'total_roles': total_roles,
                    'active_roles': active_roles,
                    'system_roles': system_roles,
                    'custom_roles': custom_roles,
                    'total_permissions': total_permissions,
                    'role_permission_distribution': [
                        {'role': name, 'permission_count': count}
                        for name, count in role_permission_counts
                    ]
                }
                
        except Exception as e:
            logger.error(f"获取角色统计失败: {e}")
            return {}
    
    def get_permission_statistics(self) -> Dict[str, Any]:
        """
        获取权限统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            with get_db_session() as session:
                # 总权限数
                total_permissions = session.query(Permission).count()
                
                # 按资源分组统计
                resource_counts = session.query(
                    Permission.resource,
                    func.count(Permission.id).label('count')
                ).group_by(Permission.resource).all()
                
                # 按分组统计
                group_counts = session.query(
                    Permission.group,
                    func.count(Permission.id).label('count')
                ).group_by(Permission.group).all()
                
                # 权限使用情况
                permission_usage = session.query(
                    Permission.name,
                    func.count(self._get_role_permission_table().c.role_id).label('role_count')
                ).outerjoin(
                    self._get_role_permission_table()
                ).group_by(Permission.id, Permission.name).all()
                
                return {
                    'total_permissions': total_permissions,
                    'resource_distribution': [
                        {'resource': resource, 'count': count}
                        for resource, count in resource_counts
                    ],
                    'group_distribution': [
                        {'group': group or '未分组', 'count': count}
                        for group, count in group_counts
                    ],
                    'permission_usage': [
                        {'permission': name, 'role_count': count}
                        for name, count in permission_usage
                    ]
                }
                
        except Exception as e:
            logger.error(f"获取权限统计失败: {e}")
            return {}    

    # ============================================================================
    # 私有辅助方法
    # ============================================================================
    
    def _validate_role_creation_data(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证角色创建数据"""
        required_fields = ['name']
        
        # 检查必需字段
        for field in required_fields:
            if field not in role_data or not role_data[field]:
                raise ValidationError(f"缺少必需字段: {field}")
        
        # 验证各字段格式
        validated_data = {}
        
        # 角色名称验证
        name_validator = StringValidator(min_length=2, max_length=50)
        validated_data['name'] = name_validator.validate(role_data['name'], '角色名称')
        
        # 可选字段
        optional_fields = ['description', 'is_active', 'is_system', 'sort_order']
        for field in optional_fields:
            if field in role_data:
                validated_data[field] = role_data[field]
        
        return validated_data
    
    def _validate_role_update_data(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证角色更新数据"""
        validated_data = {}
        
        # 验证各字段格式
        if 'name' in update_data:
            name_validator = StringValidator(min_length=2, max_length=50)
            validated_data['name'] = name_validator.validate(update_data['name'], '角色名称')
        
        # 其他可更新字段
        updatable_fields = ['description', 'is_active', 'sort_order']
        for field in updatable_fields:
            if field in update_data:
                validated_data[field] = update_data[field]
        
        return validated_data
    
    def _validate_permission_creation_data(self, permission_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证权限创建数据"""
        required_fields = ['name', 'resource', 'action']
        
        # 检查必需字段
        for field in required_fields:
            if field not in permission_data or not permission_data[field]:
                raise ValidationError(f"缺少必需字段: {field}")
        
        # 验证各字段格式
        validated_data = {}
        
        # 权限名称验证
        name_validator = StringValidator(min_length=2, max_length=100)
        validated_data['name'] = name_validator.validate(permission_data['name'], '权限名称')
        
        # 资源名称验证
        resource_validator = StringValidator(min_length=2, max_length=50)
        validated_data['resource'] = resource_validator.validate(permission_data['resource'], '资源名称')
        
        # 操作类型验证
        action_validator = StringValidator(min_length=2, max_length=50)
        validated_data['action'] = action_validator.validate(permission_data['action'], '操作类型')
        
        # 可选字段
        optional_fields = ['description', 'group', 'sort_order']
        for field in optional_fields:
            if field in permission_data:
                validated_data[field] = permission_data[field]
        
        return validated_data
    
    def _check_role_name_uniqueness(self, name: str, exclude_role_id: Optional[str] = None):
        """检查角色名称唯一性"""
        with get_db_session() as session:
            query = session.query(Role).filter(Role.name == name)
            if exclude_role_id:
                query = query.filter(Role.id != exclude_role_id)
            if query.first():
                raise BusinessLogicError(f"角色名称已存在: {name}")
    
    def _check_permission_name_uniqueness(self, name: str, exclude_permission_id: Optional[str] = None):
        """检查权限名称唯一性"""
        with get_db_session() as session:
            query = session.query(Permission).filter(Permission.name == name)
            if exclude_permission_id:
                query = query.filter(Permission.id != exclude_permission_id)
            if query.first():
                raise BusinessLogicError(f"权限名称已存在: {name}")
    
    def _get_role_permission_table(self):
        """获取角色权限关联表"""
        from sqlalchemy import Table, Column, String, ForeignKey, MetaData
        
        # 创建角色权限关联表定义
        metadata = MetaData()
        role_permission_table = Table(
            'role_permissions',
            metadata,
            Column('role_id', String(36), ForeignKey('roles.id'), primary_key=True),
            Column('permission_id', String(36), ForeignKey('permissions.id'), primary_key=True)
        )
        
        return role_permission_table
    
    def _role_has_permission(self, role_id: str, permission_id: str, session: Session) -> bool:
        """检查角色是否拥有指定权限"""
        try:
            table = self._get_role_permission_table()
            result = session.execute(
                table.select().where(
                    and_(
                        table.c.role_id == role_id,
                        table.c.permission_id == permission_id
                    )
                )
            ).first()
            return result is not None
        except Exception as e:
            logger.error(f"检查角色权限失败: {e}")
            return False
    
    def _role_has_permission_by_name(self, role_id: str, permission_name: str, session: Session) -> bool:
        """检查角色是否拥有指定名称的权限"""
        try:
            # 先获取权限ID
            permission = session.query(Permission).filter(Permission.name == permission_name).first()
            if not permission:
                return False
            
            return self._role_has_permission(role_id, permission.id, session)
        except Exception as e:
            logger.error(f"检查角色权限失败: {e}")
            return False
    
    def _create_role_permission_association(self, role_id: str, permission_id: str, session: Session):
        """创建角色权限关联"""
        try:
            table = self._get_role_permission_table()
            session.execute(
                table.insert().values(
                    role_id=role_id,
                    permission_id=permission_id
                )
            )
        except Exception as e:
            logger.error(f"创建角色权限关联失败: {e}")
            raise
    
    def _delete_role_permission_association(self, role_id: str, permission_id: str, session: Session):
        """删除角色权限关联"""
        try:
            table = self._get_role_permission_table()
            session.execute(
                table.delete().where(
                    and_(
                        table.c.role_id == role_id,
                        table.c.permission_id == permission_id
                    )
                )
            )
        except Exception as e:
            logger.error(f"删除角色权限关联失败: {e}")
            raise


# 创建全局角色服务实例
role_service = RoleService()