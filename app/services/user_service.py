"""
用户服务层

提供用户管理的业务逻辑和数据操作服务
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

from app.models.user import User
from app.models.role import Role
from app.core.extensions import get_db_session
from app.core.utils import hash_password, verify_password, generate_secure_token
from app.core.validators import validate_user_data, username_validator, email_validator, password_validator
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError
from app.core.constants import UserStatus
import logging

logger = logging.getLogger(__name__)


class UserService:
    """用户服务类 - 提供用户管理的业务逻辑"""
    
    def __init__(self, session: Optional[Session] = None):
        """
        初始化用户服务
        
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
    # 用户创建和注册
    # ============================================================================
    
    def create_user(self, user_data: Dict[str, Any], created_by: Optional[str] = None) -> User:
        """
        创建新用户
        
        Args:
            user_data: 用户数据字典
            created_by: 创建者用户ID
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            ValidationError: 数据验证失败
            BusinessLogicError: 业务逻辑错误
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证用户数据
            validated_data = self._validate_user_creation_data(user_data)
            
            # 检查用户名和邮箱唯一性
            self._check_user_uniqueness(
                username=validated_data['username'],
                email=validated_data['email']
            )
            
            # 创建用户对象
            user = User(
                username=validated_data['username'],
                email=validated_data['email'],
                password_hash=hash_password(validated_data['password']),
                full_name=validated_data.get('full_name', ''),
                phone=validated_data.get('phone'),
                avatar_url=validated_data.get('avatar_url'),
                is_active=validated_data.get('is_active', True),
                is_verified=validated_data.get('is_verified', False),
                is_superuser=validated_data.get('is_superuser', False)
            )
            
            with get_db_session() as session:
                session.add(user)
                session.commit()
                session.refresh(user)
                
                # 记录操作日志
                if created_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=created_by,
                        operation='create_user',
                        resource='user',
                        details={
                            'target_user_id': user.id,
                            'username': user.username,
                            'email': user.email
                        }
                    )
                
                logger.info(f"用户创建成功: {user.username} (ID: {user.id})")
                return user
                
        except IntegrityError as e:
            logger.error(f"用户创建失败 - 数据完整性错误: {e}")
            raise BusinessLogicError("用户名或邮箱已存在")
        except Exception as e:
            logger.error(f"用户创建失败: {e}")
            raise DatabaseError(f"用户创建失败: {str(e)}")
    
    def register_user(self, registration_data: Dict[str, Any]) -> User:
        """
        用户自主注册
        
        Args:
            registration_data: 注册数据
            
        Returns:
            User: 注册的用户对象
        """
        # 自主注册的用户默认为普通用户
        registration_data['is_superuser'] = False
        registration_data['status'] = UserStatus.ACTIVE
        
        return self.create_user(registration_data)
    
    # ============================================================================
    # 用户查询和获取
    # ============================================================================
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象或None
        """
        try:
            with get_db_session() as session:
                return session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"获取用户失败 (ID: {user_id}): {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 用户对象或None
        """
        try:
            with get_db_session() as session:
                return session.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"获取用户失败 (用户名: {username}): {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            Optional[User]: 用户对象或None
        """
        try:
            with get_db_session() as session:
                return session.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"获取用户失败 (邮箱: {email}): {e}")
            return None
    
    def get_users_list(self, 
                      page: int = 1, 
                      per_page: int = 20,
                      search: Optional[str] = None,
                      status: Optional[str] = None,
                      role_id: Optional[str] = None,
                      sort_by: str = 'created_at',
                      sort_order: str = 'desc') -> Tuple[List[User], int]:
        """
        获取用户列表（分页）
        
        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词
            status: 用户状态筛选
            role_id: 角色ID筛选
            sort_by: 排序字段
            sort_order: 排序方向
            
        Returns:
            Tuple[List[User], int]: (用户列表, 总数量)
        """
        try:
            with get_db_session() as session:
                query = session.query(User)
                
                # 搜索条件
                if search:
                    search_filter = or_(
                        User.username.ilike(f'%{search}%'),
                        User.email.ilike(f'%{search}%'),
                        User.full_name.ilike(f'%{search}%')
                    )
                    query = query.filter(search_filter)
                
                # 状态筛选
                if status:
                    query = query.filter(User.status == status)
                
                # 角色筛选
                if role_id:
                    query = query.join(User.roles).filter(Role.id == role_id)
                
                # 排序
                if hasattr(User, sort_by):
                    order_column = getattr(User, sort_by)
                    if sort_order.lower() == 'desc':
                        query = query.order_by(order_column.desc())
                    else:
                        query = query.order_by(order_column.asc())
                
                # 获取总数
                total = query.count()
                
                # 分页
                offset = (page - 1) * per_page
                users = query.offset(offset).limit(per_page).all()
                
                return users, total
                
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            raise DatabaseError(f"获取用户列表失败: {str(e)}")
    
    # ============================================================================
    # 用户更新和修改
    # ============================================================================
    
    def update_user(self, user_id: str, update_data: Dict[str, Any], 
                   updated_by: Optional[str] = None) -> User:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            update_data: 更新数据
            updated_by: 更新者用户ID
            
        Returns:
            User: 更新后的用户对象
            
        Raises:
            ValidationError: 数据验证失败
            BusinessLogicError: 业务逻辑错误
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证更新数据
            validated_data = self._validate_user_update_data(update_data)
            
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    raise BusinessLogicError(f"用户不存在: {user_id}")
                
                # 检查唯一性（排除当前用户）
                if 'username' in validated_data:
                    self._check_user_uniqueness(
                        username=validated_data['username'],
                        exclude_user_id=user_id
                    )
                
                if 'email' in validated_data:
                    self._check_user_uniqueness(
                        email=validated_data['email'],
                        exclude_user_id=user_id
                    )
                
                # 记录更新前的数据
                old_data = {
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'status': user.status
                }
                
                # 更新用户信息
                for field, value in validated_data.items():
                    if hasattr(user, field):
                        setattr(user, field, value)
                
                user.updated_at = datetime.now(timezone.utc)
                user.updated_by = updated_by
                
                session.commit()
                session.refresh(user)
                
                # 记录操作日志
                if updated_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=updated_by,
                        operation='update_user',
                        resource='user',
                        details={
                            'target_user_id': user.id,
                            'old_data': old_data,
                            'new_data': validated_data
                        }
                    )
                
                logger.info(f"用户更新成功: {user.username} (ID: {user.id})")
                return user
                
        except IntegrityError as e:
            logger.error(f"用户更新失败 - 数据完整性错误: {e}")
            raise BusinessLogicError("用户名或邮箱已存在")
        except Exception as e:
            logger.error(f"用户更新失败: {e}")
            raise DatabaseError(f"用户更新失败: {str(e)}")
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> User:
        """
        更新用户个人资料（用户自己更新）
        
        Args:
            user_id: 用户ID
            profile_data: 个人资料数据
            
        Returns:
            User: 更新后的用户对象
        """
        # 用户只能更新特定字段
        allowed_fields = ['full_name', 'phone', 'avatar_url']
        filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        
        return self.update_user(user_id, filtered_data, updated_by=user_id)
    
    # ============================================================================
    # 用户状态管理
    # ============================================================================
    
    def activate_user(self, user_id: str, activated_by: Optional[str] = None) -> User:
        """
        激活用户
        
        Args:
            user_id: 用户ID
            activated_by: 操作者用户ID
            
        Returns:
            User: 激活后的用户对象
        """
        return self.update_user(
            user_id, 
            {'status': UserStatus.ACTIVE}, 
            updated_by=activated_by
        )
    
    def deactivate_user(self, user_id: str, deactivated_by: Optional[str] = None) -> User:
        """
        停用用户
        
        Args:
            user_id: 用户ID
            deactivated_by: 操作者用户ID
            
        Returns:
            User: 停用后的用户对象
        """
        return self.update_user(
            user_id, 
            {'status': UserStatus.INACTIVE}, 
            updated_by=deactivated_by
        )
    
    def lock_user(self, user_id: str, locked_by: Optional[str] = None, 
                 reason: Optional[str] = None) -> User:
        """
        锁定用户
        
        Args:
            user_id: 用户ID
            locked_by: 操作者用户ID
            reason: 锁定原因
            
        Returns:
            User: 锁定后的用户对象
        """
        update_data = {'status': UserStatus.LOCKED}
        if reason:
            update_data['lock_reason'] = reason
        
        return self.update_user(user_id, update_data, updated_by=locked_by)
    
    def unlock_user(self, user_id: str, unlocked_by: Optional[str] = None) -> User:
        """
        解锁用户
        
        Args:
            user_id: 用户ID
            unlocked_by: 操作者用户ID
            
        Returns:
            User: 解锁后的用户对象
        """
        return self.update_user(
            user_id, 
            {'status': UserStatus.ACTIVE, 'lock_reason': None}, 
            updated_by=unlocked_by
        )
    
    # ============================================================================
    # 密码管理
    # ============================================================================
    
    def change_password(self, user_id: str, old_password: str, 
                       new_password: str) -> bool:
        """
        用户修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 是否修改成功
            
        Raises:
            ValidationError: 密码验证失败
            BusinessLogicError: 业务逻辑错误
        """
        try:
            # 验证新密码格式
            password_validator.validate(new_password, '新密码')
            
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    raise BusinessLogicError(f"用户不存在: {user_id}")
                
                # 验证旧密码
                if not verify_password(old_password, user.password_hash):
                    raise BusinessLogicError("原密码不正确")
                
                # 更新密码
                user.password_hash = hash_password(new_password)
                user.updated_at = datetime.now(timezone.utc)
                user.updated_by = user_id
                
                session.commit()
                
                # 记录操作日志
                from app.services.log_service import log_service
                log_service.create_operation_log(
                    user_id=user_id,
                    operation='change_password',
                    resource='user',
                    details={'target_user_id': user_id}
                )
                
                logger.info(f"用户密码修改成功: {user.username}")
                return True
                
        except Exception as e:
            logger.error(f"密码修改失败: {e}")
            raise
    
    def reset_password(self, user_id: str, new_password: Optional[str] = None,
                      reset_by: Optional[str] = None) -> str:
        """
        重置用户密码（管理员操作）
        
        Args:
            user_id: 用户ID
            new_password: 新密码，如果不提供则自动生成
            reset_by: 操作者用户ID
            
        Returns:
            str: 新密码（明文）
            
        Raises:
            BusinessLogicError: 业务逻辑错误
        """
        try:
            if not new_password:
                new_password = generate_secure_token(12)
            
            # 验证新密码格式
            password_validator.validate(new_password, '新密码')
            
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    raise BusinessLogicError(f"用户不存在: {user_id}")
                
                # 更新密码
                user.password_hash = hash_password(new_password)
                user.updated_at = datetime.now(timezone.utc)
                user.updated_by = reset_by
                
                session.commit()
                
                # 记录操作日志
                if reset_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=reset_by,
                        operation='reset_password',
                        resource='user',
                        details={'target_user_id': user_id}
                    )
                
                logger.info(f"用户密码重置成功: {user.username}")
                return new_password
                
        except Exception as e:
            logger.error(f"密码重置失败: {e}")
            raise DatabaseError(f"密码重置失败: {str(e)}")
    
    # ============================================================================
    # 用户删除
    # ============================================================================
    
    def delete_user(self, user_id: str, deleted_by: Optional[str] = None,
                   soft_delete: bool = True) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            deleted_by: 操作者用户ID
            soft_delete: 是否软删除
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            BusinessLogicError: 业务逻辑错误
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    raise BusinessLogicError(f"用户不存在: {user_id}")
                
                # 检查是否可以删除
                if user.is_superuser and not self._can_delete_superuser(user_id, deleted_by):
                    raise BusinessLogicError("无法删除超级管理员用户")
                
                if soft_delete:
                    # 软删除
                    user.status = UserStatus.DELETED
                    user.deleted_at = datetime.now(timezone.utc)
                    user.deleted_by = deleted_by
                    session.commit()
                else:
                    # 硬删除
                    session.delete(user)
                    session.commit()
                
                # 记录操作日志
                if deleted_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=deleted_by,
                        operation='delete_user',
                        resource='user',
                        details={
                            'target_user_id': user_id,
                            'username': user.username,
                            'soft_delete': soft_delete
                        }
                    )
                
                logger.info(f"用户删除成功: {user.username} (软删除: {soft_delete})")
                return True
                
        except Exception as e:
            logger.error(f"用户删除失败: {e}")
            raise DatabaseError(f"用户删除失败: {str(e)}")
    
    # ============================================================================
    # 用户角色管理
    # ============================================================================
    
    def assign_role_to_user(self, user_id: str, role_id: str, 
                           assigned_by: Optional[str] = None) -> bool:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            assigned_by: 操作者用户ID
            
        Returns:
            bool: 是否分配成功
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                role = session.query(Role).filter(Role.id == role_id).first()
                
                if not user:
                    raise BusinessLogicError(f"用户不存在: {user_id}")
                if not role:
                    raise BusinessLogicError(f"角色不存在: {role_id}")
                
                # 检查是否已经有该角色
                if role in user.roles:
                    logger.warning(f"用户 {user.username} 已经拥有角色 {role.name}")
                    return True
                
                # 分配角色
                user.roles.append(role)
                session.commit()
                
                # 记录操作日志
                if assigned_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=assigned_by,
                        operation='assign_role',
                        resource='user',
                        details={
                            'target_user_id': user_id,
                            'role_id': role_id,
                            'role_name': role.name
                        }
                    )
                
                logger.info(f"角色分配成功: 用户 {user.username} 获得角色 {role.name}")
                return True
                
        except Exception as e:
            logger.error(f"角色分配失败: {e}")
            raise DatabaseError(f"角色分配失败: {str(e)}")
    
    def remove_role_from_user(self, user_id: str, role_id: str,
                             removed_by: Optional[str] = None) -> bool:
        """
        移除用户角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            removed_by: 操作者用户ID
            
        Returns:
            bool: 是否移除成功
        """
        try:
            with get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                role = session.query(Role).filter(Role.id == role_id).first()
                
                if not user:
                    raise BusinessLogicError(f"用户不存在: {user_id}")
                if not role:
                    raise BusinessLogicError(f"角色不存在: {role_id}")
                
                # 检查是否有该角色
                if role not in user.roles:
                    logger.warning(f"用户 {user.username} 没有角色 {role.name}")
                    return True
                
                # 移除角色
                user.roles.remove(role)
                session.commit()
                
                # 记录操作日志
                if removed_by:
                    from app.services.log_service import log_service
                    log_service.create_operation_log(
                        user_id=removed_by,
                        operation='remove_role',
                        resource='user',
                        details={
                            'target_user_id': user_id,
                            'role_id': role_id,
                            'role_name': role.name
                        }
                    )
                
                logger.info(f"角色移除成功: 用户 {user.username} 失去角色 {role.name}")
                return True
                
        except Exception as e:
            logger.error(f"角色移除失败: {e}")
            raise DatabaseError(f"角色移除失败: {str(e)}")
    
    # ============================================================================
    # 用户统计和分析
    # ============================================================================
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            with get_db_session() as session:
                # 总用户数
                total_users = session.query(User).count()
                
                # 活跃用户数
                active_users = session.query(User).filter(
                    User.status == UserStatus.ACTIVE
                ).count()
                
                # 各状态用户数
                status_counts = {}
                for status in [UserStatus.ACTIVE, UserStatus.INACTIVE, UserStatus.LOCKED, UserStatus.DELETED]:
                    count = session.query(User).filter(User.status == status).count()
                    status_counts[status] = count
                
                # 超级用户数
                superuser_count = session.query(User).filter(User.is_superuser == True).count()
                
                # 最近注册用户数（7天内）
                from datetime import timedelta
                week_ago = datetime.now(timezone.utc) - timedelta(days=7)
                recent_registrations = session.query(User).filter(
                    User.created_at >= week_ago
                ).count()
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'status_distribution': status_counts,
                    'superuser_count': superuser_count,
                    'recent_registrations': recent_registrations,
                    'activity_rate': round(active_users / total_users * 100, 2) if total_users > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return {}
    
    def get_user_login_history(self, user_id: str, limit: int = 50):
        """
        获取用户登录历史
        
        Args:
            user_id: 用户ID
            limit: 返回记录数限制
            
        Returns:
            登录日志列表
        """
        try:
            from app.services.log_service import log_service
            logs, _ = log_service.get_login_logs_by_user(user_id, page=1, per_page=limit)
            return logs
        except Exception as e:
            logger.error(f"获取用户登录历史失败: {e}")
            return []
    
    # ============================================================================
    # 权限和角色检查
    # ============================================================================
    
    def check_user_permission(self, user_id: str, permission_name: str) -> bool:
        """
        检查用户是否拥有指定权限
        
        Args:
            user_id: 用户ID
            permission_name: 权限名称
            
        Returns:
            bool: 是否拥有权限
        """
        try:
            with get_db_session() as session:
                # 通过用户角色关联和角色权限关联查询
                from app.models.associations import UserRole, RolePermission
                from app.models.permission import Permission
                
                exists = session.query(RolePermission).join(
                    Permission, Permission.id == RolePermission.permission_id
                ).join(
                    UserRole, UserRole.role_id == RolePermission.role_id
                ).filter(
                    UserRole.user_id == user_id,
                    Permission.name == permission_name,
                    RolePermission.is_deleted == False,
                    UserRole.is_deleted == False,
                    Permission.is_deleted == False
                ).first()
                
                return exists is not None
        except Exception as e:
            logger.error(f"检查用户权限失败: {e}")
            return False
    
    def check_user_role(self, user_id: str, role_name: str) -> bool:
        """
        检查用户是否拥有指定角色
        
        Args:
            user_id: 用户ID
            role_name: 角色名称
            
        Returns:
            bool: 是否拥有角色
        """
        try:
            with get_db_session() as session:
                from app.models.associations import UserRole
                from app.models.role import Role
                
                exists = session.query(UserRole).join(
                    Role, Role.id == UserRole.role_id
                ).filter(
                    UserRole.user_id == user_id,
                    Role.name == role_name,
                    UserRole.is_deleted == False,
                    Role.is_deleted == False
                ).first()
                
                return exists is not None
        except Exception as e:
            logger.error(f"检查用户角色失败: {e}")
            return False
    
    def is_user_admin(self, user_id: str) -> bool:
        """
        检查用户是否为管理员
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否为管理员
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            # 检查是否为超级用户
            if user.is_superuser:
                return True
            
            # 检查是否有admin角色
            return self.check_user_role(user_id, 'admin')
        except Exception as e:
            logger.error(f"检查用户管理员权限失败: {e}")
            return False
    
    def get_user_roles(self, user_id: str):
        """
        获取用户的所有角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Role]: 角色列表
        """
        try:
            with get_db_session() as session:
                from app.models.associations import UserRole
                from app.models.role import Role
                
                roles = session.query(Role).join(
                    UserRole, Role.id == UserRole.role_id
                ).filter(
                    UserRole.user_id == user_id,
                    UserRole.is_deleted == False,
                    Role.is_deleted == False
                ).all()
                
                return roles
        except Exception as e:
            logger.error(f"获取用户角色失败: {e}")
            return []
    
    # ============================================================================
    # 私有辅助方法
    # ============================================================================
    
    def _validate_user_creation_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证用户创建数据"""
        required_fields = ['username', 'email', 'password']
        
        # 检查必需字段
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValidationError(f"缺少必需字段: {field}")
        
        # 验证各字段格式
        validated_data = {}
        
        # 用户名验证
        validated_data['username'] = username_validator.validate(
            user_data['username'], '用户名'
        )
        
        # 邮箱验证
        validated_data['email'] = email_validator.validate(
            user_data['email'], '邮箱'
        )
        
        # 密码验证
        validated_data['password'] = password_validator.validate(
            user_data['password'], '密码'
        )
        
        # 可选字段
        optional_fields = ['full_name', 'phone', 'avatar_url', 'status', 'is_superuser']
        for field in optional_fields:
            if field in user_data:
                validated_data[field] = user_data[field]
        
        return validated_data
    
    def _validate_user_update_data(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证用户更新数据"""
        validated_data = {}
        
        # 验证各字段格式
        if 'username' in update_data:
            validated_data['username'] = username_validator.validate(
                update_data['username'], '用户名'
            )
        
        if 'email' in update_data:
            validated_data['email'] = email_validator.validate(
                update_data['email'], '邮箱'
            )
        
        # 其他可更新字段
        updatable_fields = ['full_name', 'phone', 'avatar_url', 'status', 'is_superuser']
        for field in updatable_fields:
            if field in update_data:
                validated_data[field] = update_data[field]
        
        return validated_data
    
    def _check_user_uniqueness(self, username: Optional[str] = None, 
                              email: Optional[str] = None,
                              exclude_user_id: Optional[str] = None):
        """检查用户名和邮箱唯一性"""
        with get_db_session() as session:
            if username:
                query = session.query(User).filter(User.username == username)
                if exclude_user_id:
                    query = query.filter(User.id != exclude_user_id)
                if query.first():
                    raise BusinessLogicError(f"用户名已存在: {username}")
            
            if email:
                query = session.query(User).filter(User.email == email)
                if exclude_user_id:
                    query = query.filter(User.id != exclude_user_id)
                if query.first():
                    raise BusinessLogicError(f"邮箱已存在: {email}")
    
    def _can_delete_superuser(self, user_id: str, deleted_by: Optional[str]) -> bool:
        """检查是否可以删除超级用户"""
        if not deleted_by:
            return False
        
        # 只有超级用户才能删除超级用户
        with get_db_session() as session:
            deleter = session.query(User).filter(User.id == deleted_by).first()
            if not deleter or not deleter.is_superuser:
                return False
            
            # 不能删除自己
            if user_id == deleted_by:
                return False
            
            # 确保至少保留一个超级用户
            superuser_count = session.query(User).filter(
                and_(User.is_superuser == True, User.status != UserStatus.DELETED)
            ).count()
            
            return superuser_count > 1


# 创建全局用户服务实例
user_service = UserService()