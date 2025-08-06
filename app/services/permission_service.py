"""
权限服务层

提供权限管理的业务逻辑和数据操作服务
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

from app.models.permission import Permission
from app.models.role import Role
from app.core.extensions import get_db_session
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError
from app.core.constants import PermissionType
import logging

logger = logging.getLogger(__name__)


class PermissionService:
    """权限服务类 - 提供权限管理的业务逻辑"""
    
    def __init__(self, session: Optional[Session] = None):
        """
        初始化权限服务
        
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
    # 权限创建和管理
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
            
        Raises:
            ValidationError: 数据验证失败
            BusinessLogicError: 业务逻辑错误
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证权限数据
            validated_data = self._validate_permission_creation_data(permission_data)
            
            # 检查权限名称唯一性
            self._check_permission_uniqueness(validated_data['name'])
            
            # 创建权限对象
            permission = Permission(
                name=validated_data['name'],
                resource=validated_data['resource'],
                action=validated_data['action'],
                description=validated_data.get('description', ''),
                group=validated_data.get('group'),
                sort_order=validated_data.get('sort_order', "0")
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
    
    # ============================================================================
    # 权限查询和获取
    # ============================================================================
    
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
                return session.query(Permission).filter(
                    Permission.id == permission_id
                ).first()
        except Exception as e:
            logger.error(f"获取权限失败 (ID: {permission_id}): {e}")
            return None
    
    def get_permission_by_name(self, permission_name: str) -> Optional[Permission]:
        """
        根据权限名称获取权限
        
        Args:
            permission_name: 权限名称
            
        Returns:
            Optional[Permission]: 权限对象或None
        """
        try:
            with get_db_session() as session:
                return session.query(Permission).filter(
                    Permission.name == permission_name
                ).first()
        except Exception as e:
            logger.error(f"获取权限失败 (名称: {permission_name}): {e}")
            return None
    
    def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        """
        根据资源获取权限列表
        
        Args:
            resource: 资源名称
            
        Returns:
            List[Permission]: 权限列表
        """
        try:
            with get_db_session() as session:
                return session.query(Permission).filter(
                    Permission.resource == resource
                ).all()
        except Exception as e:
            logger.error(f"获取资源权限失败 (资源: {resource}): {e}")
            return []
    
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
    # 权限更新和修改
    # ============================================================================
    
    def update_permission(self, permission_id: str, update_data: Dict[str, Any], 
                         updated_by: Optional[str] = None) -> Permission:
        """
        更新权限信息
        
        Args:
            permission_id: 权限ID
            update_data: 更新数据
            updated_by: 更新者用户ID
            
        Returns:
            Permission: 更新后的权限对象
            
        Raises:
            ValidationError: 数据验证失败
            BusinessLogicError: 业务逻辑错误
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证更新数据
            validated_data = self._validate_permission_update_data(update_data)
            
            with get_db_session() as session:
                permission = session.query(Permission).filter(
                    Permission.id == permission_id
                ).first()
                if not permission:
                    raise BusinessLogicError(f"权限不存在: {permission_id}")
                
                # 检查名称唯一性（排除当前权限）
                if 'name' in validated_data:
                    self._check_permission_uniqueness(
                        validated_data['name'],
                        exclude_permission_id=permission_id
                    )
                
                # 记录更新前的数据
                old_data = {
                    'name': permission.name,
                    'description': permission.description,
                    'resource': permission.resource,
                    'action': permission.action
                }
                
                # 更新权限信息
                for field, value in validated_data.items():
                    if hasattr(permission, field):
                        setattr(permission, field, value)
                
                permission.updated_at = datetime.now(timezone.utc)
                permission.updated_by = updated_by
                
                session.commit()
                session.refresh(permission)
                
                # 记录操作日志
                if updated_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=updated_by,
                        operation='update_permission',
                        resource='permission',
                        details={
                            'permission_id': permission.id,
                            'old_data': old_data,
                            'new_data': validated_data
                        }
                    )
                
                logger.info(f"权限更新成功: {permission.name} (ID: {permission.id})")
                return permission
                
        except IntegrityError as e:
            logger.error(f"权限更新失败 - 数据完整性错误: {e}")
            raise BusinessLogicError("权限名称已存在")
        except Exception as e:
            logger.error(f"权限更新失败: {e}")
            raise DatabaseError(f"权限更新失败: {str(e)}")
    
    # ============================================================================
    # 权限删除
    # ============================================================================
    
    def delete_permission(self, permission_id: str, deleted_by: Optional[str] = None,
                         soft_delete: bool = True) -> bool:
        """
        删除权限
        
        Args:
            permission_id: 权限ID
            deleted_by: 操作者用户ID
            soft_delete: 是否软删除
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            BusinessLogicError: 业务逻辑错误
        """
        try:
            with get_db_session() as session:
                permission = session.query(Permission).filter(
                    Permission.id == permission_id
                ).first()
                if not permission:
                    raise BusinessLogicError(f"权限不存在: {permission_id}")
                
                # 检查是否有角色使用该权限
                from app.models.associations import RolePermission
                role_count = session.query(RolePermission).filter(
                    RolePermission.permission_id == permission_id,
                    RolePermission.is_deleted == False
                ).count()
                
                if role_count > 0:
                    raise BusinessLogicError(f"权限正在被 {role_count} 个角色使用，无法删除")
                
                if soft_delete:
                    # 软删除
                    permission.is_deleted = True
                    permission.deleted_at = datetime.now(timezone.utc)
                    permission.deleted_by = deleted_by
                    session.commit()
                else:
                    # 硬删除
                    session.delete(permission)
                    session.commit()
                
                # 记录操作日志
                if deleted_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=deleted_by,
                        operation='delete_permission',
                        resource='permission',
                        details={
                            'permission_id': permission_id,
                            'permission_name': permission.name,
                            'soft_delete': soft_delete
                        }
                    )
                
                logger.info(f"权限删除成功: {permission.name} (软删除: {soft_delete})")
                return True
                
        except Exception as e:
            logger.error(f"权限删除失败: {e}")
            raise DatabaseError(f"权限删除失败: {str(e)}")
    
    # ============================================================================
    # 权限统计和分析
    # ============================================================================
    
    def get_permission_statistics(self) -> Dict[str, Any]:
        """
        获取权限统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            with get_db_session() as session:
                # 总权限数
                total_permissions = session.query(Permission).filter(
                    Permission.is_deleted == False
                ).count()
                
                # 各资源权限数
                resource_counts = {}
                resources = session.query(Permission.resource).filter(
                    Permission.is_deleted == False
                ).distinct().all()
                for (resource,) in resources:
                    count = session.query(Permission).filter(
                        and_(
                            Permission.resource == resource,
                            Permission.is_deleted == False
                        )
                    ).count()
                    resource_counts[resource] = count
                
                # 各分组权限数
                group_counts = {}
                groups = session.query(Permission.group).filter(
                    and_(
                        Permission.group.isnot(None),
                        Permission.is_deleted == False
                    )
                ).distinct().all()
                for (group,) in groups:
                    count = session.query(Permission).filter(
                        and_(
                            Permission.group == group,
                            Permission.is_deleted == False
                        )
                    ).count()
                    group_counts[group] = count
                
                # 最近创建权限数（7天内）
                from datetime import timedelta
                week_ago = datetime.now(timezone.utc) - timedelta(days=7)
                recent_permissions = session.query(Permission).filter(
                    and_(
                        Permission.created_at >= week_ago,
                        Permission.is_deleted == False
                    )
                ).count()
                
                return {
                    'total_permissions': total_permissions,
                    'resource_distribution': resource_counts,
                    'group_distribution': group_counts,
                    'recent_permissions': recent_permissions
                }
                
        except Exception as e:
            logger.error(f"获取权限统计失败: {e}")
            return {}
    
    def get_resource_permissions_tree(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取按资源分组的权限树
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 权限树结构
        """
        try:
            with get_db_session() as session:
                permissions = session.query(Permission).filter(
                    Permission.is_deleted == False
                ).order_by(Permission.resource, Permission.action).all()
                
                tree = {}
                for permission in permissions:
                    if permission.resource not in tree:
                        tree[permission.resource] = []
                    
                    tree[permission.resource].append({
                        'id': permission.id,
                        'name': permission.name,
                        'action': permission.action,
                        'description': permission.description,
                        'group': permission.group
                    })
                
                return tree
                
        except Exception as e:
            logger.error(f"获取权限树失败: {e}")
            return {}
    
    # ============================================================================
    # 批量操作
    # ============================================================================
    
    def batch_create_permissions(self, permissions_data: List[Dict[str, Any]],
                               created_by: Optional[str] = None) -> Dict[str, Any]:
        """
        批量创建权限
        
        Args:
            permissions_data: 权限数据列表
            created_by: 创建者用户ID
            
        Returns:
            Dict[str, Any]: 创建结果统计
        """
        success_count = 0
        failed_permissions = []
        created_permissions = []
        
        for permission_data in permissions_data:
            try:
                permission = self.create_permission(permission_data, created_by)
                created_permissions.append(permission)
                success_count += 1
            except Exception as e:
                failed_permissions.append({
                    'permission_data': permission_data,
                    'error': str(e)
                })
        
        return {
            'total': len(permissions_data),
            'success': success_count,
            'failed': len(failed_permissions),
            'created_permissions': created_permissions,
            'failed_permissions': failed_permissions
        }
    
    # ============================================================================
    # 私有辅助方法
    # ============================================================================
    
    def _validate_permission_creation_data(self, permission_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证权限创建数据"""
        required_fields = ['name', 'resource', 'action']
        
        # 检查必需字段
        for field in required_fields:
            if field not in permission_data or not permission_data[field]:
                raise ValidationError(f"缺少必需字段: {field}")
        
        # 验证权限名称格式
        name = permission_data['name'].strip()
        if len(name) < 2 or len(name) > 100:
            raise ValidationError("权限名称长度必须在2-100个字符之间")
        
        # 验证资源和动作格式
        resource = permission_data['resource'].strip()
        action = permission_data['action'].strip()
        
        if not resource or not action:
            raise ValidationError("资源和动作不能为空")
        
        # 构建标准权限名称（如果没有提供）
        if name == f"{resource}:{action}":
            # 使用标准格式
            pass
        elif ':' not in name:
            # 如果名称中没有冒号，使用resource:action格式
            name = f"{resource}:{action}"
        
        validated_data = {
            'name': name,
            'resource': resource,
            'action': action,
            'description': permission_data.get('description', ''),
            'group': permission_data.get('group'),
            'sort_order': permission_data.get('sort_order', "0")
        }
        
        return validated_data
    
    def _validate_permission_update_data(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证权限更新数据"""
        validated_data = {}
        
        # 验证权限名称
        if 'name' in update_data:
            name = update_data['name'].strip()
            if len(name) < 2 or len(name) > 100:
                raise ValidationError("权限名称长度必须在2-100个字符之间")
            validated_data['name'] = name
        
        # 验证资源和动作
        if 'resource' in update_data:
            resource = update_data['resource'].strip()
            if not resource:
                raise ValidationError("资源不能为空")
            validated_data['resource'] = resource
        
        if 'action' in update_data:
            action = update_data['action'].strip()
            if not action:
                raise ValidationError("动作不能为空")
            validated_data['action'] = action
        
        # 其他可更新字段
        updatable_fields = ['description', 'group', 'sort_order']
        for field in updatable_fields:
            if field in update_data:
                validated_data[field] = update_data[field]
        
        return validated_data
    
    def _check_permission_uniqueness(self, permission_name: str, 
                                   exclude_permission_id: Optional[str] = None):
        """检查权限名称唯一性"""
        with get_db_session() as session:
            query = session.query(Permission).filter(
                and_(
                    Permission.name == permission_name,
                    Permission.is_deleted == False
                )
            )
            if exclude_permission_id:
                query = query.filter(Permission.id != exclude_permission_id)
            if query.first():
                raise BusinessLogicError(f"权限名称已存在: {permission_name}")


# 创建全局权限服务实例
permission_service = PermissionService()