"""
日志服务层

提供登录日志和操作日志的业务逻辑和数据操作服务
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

from app.models.logs import LoginLog, OperationLog
from app.models.user import User
from app.core.extensions import get_db_session
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError
import logging

logger = logging.getLogger(__name__)


class LogService:
    """日志服务类 - 提供日志管理的业务逻辑"""
    
    def __init__(self, session: Optional[Session] = None):
        """
        初始化日志服务
        
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
    # 登录日志管理
    # ============================================================================
    
    def create_login_log(self, user_id: Optional[str] = None, 
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None, 
                        status: str = 'failed') -> LoginLog:
        """
        创建登录日志
        
        Args:
            user_id: 用户ID
            ip_address: IP地址
            user_agent: 用户代理字符串
            status: 登录状态 ('success' 或 'failed')
            
        Returns:
            LoginLog: 创建的登录日志对象
            
        Raises:
            ValidationError: 数据验证失败
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证状态值
            if status not in ['success', 'failed']:
                raise ValidationError("登录状态必须是 'success' 或 'failed'")
            
            # 创建登录日志对象
            login_log = LoginLog(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                login_time=datetime.now(timezone.utc)
            )
            
            with get_db_session() as session:
                session.add(login_log)
                session.commit()
                session.refresh(login_log)
                
                log_type = "成功" if status == 'success' else "失败"
                logger.info(f"创建登录日志: 用户 {user_id} 登录{log_type}")
                return login_log
                
        except Exception as e:
            logger.error(f"创建登录日志失败: {e}")
            raise DatabaseError(f"创建登录日志失败: {str(e)}")
    
    def update_logout_time(self, login_log_id: str) -> LoginLog:
        """
        更新登出时间
        
        Args:
            login_log_id: 登录日志ID
            
        Returns:
            LoginLog: 更新后的登录日志对象
            
        Raises:
            BusinessLogicError: 业务逻辑错误
            DatabaseError: 数据库操作失败
        """
        try:
            with get_db_session() as session:
                login_log = session.query(LoginLog).filter(
                    LoginLog.id == login_log_id
                ).first()
                
                if not login_log:
                    raise BusinessLogicError(f"登录日志不存在: {login_log_id}")
                
                login_log.logout_time = datetime.now(timezone.utc)
                session.commit()
                session.refresh(login_log)
                
                logger.info(f"更新登出时间: 用户 {login_log.user_id}")
                return login_log
                
        except Exception as e:
            logger.error(f"更新登出时间失败: {e}")
            raise DatabaseError(f"更新登出时间失败: {str(e)}")
    
    def get_login_logs_by_user(self, user_id: str, 
                              page: int = 1, 
                              per_page: int = 50) -> Tuple[List[LoginLog], int]:
        """
        获取用户的登录日志
        
        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            
        Returns:
            Tuple[List[LoginLog], int]: (登录日志列表, 总数量)
        """
        try:
            with get_db_session() as session:
                query = session.query(LoginLog).filter(LoginLog.user_id == user_id)
                
                # 获取总数
                total = query.count()
                
                # 分页和排序
                offset = (page - 1) * per_page
                logs = query.order_by(LoginLog.login_time.desc()).offset(offset).limit(per_page).all()
                
                return logs, total
                
        except Exception as e:
            logger.error(f"获取用户登录日志失败: {e}")
            return [], 0
    
    def get_recent_login_logs(self, hours: int = 24, 
                             limit: int = 100) -> List[LoginLog]:
        """
        获取最近的登录日志
        
        Args:
            hours: 时间范围（小时）
            limit: 返回记录数限制
            
        Returns:
            List[LoginLog]: 登录日志列表
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            with get_db_session() as session:
                logs = session.query(LoginLog).filter(
                    LoginLog.login_time >= cutoff_time
                ).order_by(
                    LoginLog.login_time.desc()
                ).limit(limit).all()
                
                return logs
                
        except Exception as e:
            logger.error(f"获取最近登录日志失败: {e}")
            return []
    
    def get_failed_login_attempts(self, user_id: Optional[str] = None, 
                                 ip_address: Optional[str] = None,
                                 hours: int = 1) -> List[LoginLog]:
        """
        获取失败的登录尝试
        
        Args:
            user_id: 用户ID（可选）
            ip_address: IP地址（可选）
            hours: 时间范围（小时）
            
        Returns:
            List[LoginLog]: 失败登录日志列表
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            with get_db_session() as session:
                query = session.query(LoginLog).filter(
                    and_(
                        LoginLog.status == 'failed',
                        LoginLog.login_time >= cutoff_time
                    )
                )
                
                if user_id:
                    query = query.filter(LoginLog.user_id == user_id)
                
                if ip_address:
                    query = query.filter(LoginLog.ip_address == ip_address)
                
                return query.order_by(LoginLog.login_time.desc()).all()
                
        except Exception as e:
            logger.error(f"获取失败登录尝试失败: {e}")
            return []
    
    def get_login_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        获取登录统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
            
            with get_db_session() as session:
                # 总登录次数
                total_logins = session.query(LoginLog).filter(
                    LoginLog.login_time >= cutoff_time
                ).count()
                
                # 成功登录次数
                successful_logins = session.query(LoginLog).filter(
                    and_(
                        LoginLog.status == 'success',
                        LoginLog.login_time >= cutoff_time
                    )
                ).count()
                
                # 失败登录次数
                failed_logins = session.query(LoginLog).filter(
                    and_(
                        LoginLog.status == 'failed',
                        LoginLog.login_time >= cutoff_time
                    )
                ).count()
                
                # 独立用户数
                unique_users = session.query(LoginLog.user_id).filter(
                    and_(
                        LoginLog.user_id.isnot(None),
                        LoginLog.login_time >= cutoff_time
                    )
                ).distinct().count()
                
                # 独立IP数
                unique_ips = session.query(LoginLog.ip_address).filter(
                    and_(
                        LoginLog.ip_address.isnot(None),
                        LoginLog.login_time >= cutoff_time
                    )
                ).distinct().count()
                
                return {
                    'period_days': days,
                    'total_logins': total_logins,
                    'successful_logins': successful_logins,
                    'failed_logins': failed_logins,
                    'success_rate': round(successful_logins / total_logins * 100, 2) if total_logins > 0 else 0,
                    'unique_users': unique_users,
                    'unique_ips': unique_ips
                }
                
        except Exception as e:
            logger.error(f"获取登录统计失败: {e}")
            return {}
    
    # ============================================================================
    # 操作日志管理
    # ============================================================================
    
    def create_operation_log(self, user_id: Optional[str] = None, 
                           operation: Optional[str] = None,
                           resource: Optional[str] = None, 
                           details: Optional[Dict[str, Any]] = None,
                           ip_address: Optional[str] = None) -> OperationLog:
        """
        创建操作日志
        
        Args:
            user_id: 操作用户ID
            operation: 操作类型
            resource: 操作资源
            details: 操作详情
            ip_address: 客户端IP地址
            
        Returns:
            OperationLog: 创建的操作日志对象
            
        Raises:
            ValidationError: 数据验证失败
            DatabaseError: 数据库操作失败
        """
        try:
            # 验证必要字段
            if not operation:
                raise ValidationError("操作类型不能为空")
            
            if not resource:
                raise ValidationError("操作资源不能为空")
            
            # 创建操作日志对象
            operation_log = OperationLog(
                user_id=user_id,
                operation=operation,
                resource=resource,
                details=details,
                ip_address=ip_address,
                created_at=datetime.now(timezone.utc)
            )
            
            with get_db_session() as session:
                session.add(operation_log)
                session.commit()
                session.refresh(operation_log)
                
                logger.info(f"创建操作日志: 用户 {user_id} {operation} {resource}")
                return operation_log
                
        except Exception as e:
            logger.error(f"创建操作日志失败: {e}")
            raise DatabaseError(f"创建操作日志失败: {str(e)}")
    
    def get_operation_logs_by_user(self, user_id: str, 
                                  page: int = 1, 
                                  per_page: int = 50) -> Tuple[List[OperationLog], int]:
        """
        获取用户的操作日志
        
        Args:
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            
        Returns:
            Tuple[List[OperationLog], int]: (操作日志列表, 总数量)
        """
        try:
            with get_db_session() as session:
                query = session.query(OperationLog).filter(OperationLog.user_id == user_id)
                
                # 获取总数
                total = query.count()
                
                # 分页和排序
                offset = (page - 1) * per_page
                logs = query.order_by(OperationLog.created_at.desc()).offset(offset).limit(per_page).all()
                
                return logs, total
                
        except Exception as e:
            logger.error(f"获取用户操作日志失败: {e}")
            return [], 0
    
    def get_operation_logs_by_resource(self, resource: str, 
                                      page: int = 1, 
                                      per_page: int = 50) -> Tuple[List[OperationLog], int]:
        """
        获取资源的操作日志
        
        Args:
            resource: 资源名称
            page: 页码
            per_page: 每页数量
            
        Returns:
            Tuple[List[OperationLog], int]: (操作日志列表, 总数量)
        """
        try:
            with get_db_session() as session:
                query = session.query(OperationLog).filter(OperationLog.resource == resource)
                
                # 获取总数
                total = query.count()
                
                # 分页和排序
                offset = (page - 1) * per_page
                logs = query.order_by(OperationLog.created_at.desc()).offset(offset).limit(per_page).all()
                
                return logs, total
                
        except Exception as e:
            logger.error(f"获取资源操作日志失败: {e}")
            return [], 0
    
    def get_operation_logs_by_operation(self, operation: str, 
                                       page: int = 1, 
                                       per_page: int = 50) -> Tuple[List[OperationLog], int]:
        """
        获取指定操作类型的日志
        
        Args:
            operation: 操作类型
            page: 页码
            per_page: 每页数量
            
        Returns:
            Tuple[List[OperationLog], int]: (操作日志列表, 总数量)
        """
        try:
            with get_db_session() as session:
                query = session.query(OperationLog).filter(OperationLog.operation == operation)
                
                # 获取总数
                total = query.count()
                
                # 分页和排序
                offset = (page - 1) * per_page
                logs = query.order_by(OperationLog.created_at.desc()).offset(offset).limit(per_page).all()
                
                return logs, total
                
        except Exception as e:
            logger.error(f"获取操作类型日志失败: {e}")
            return [], 0
    
    def get_recent_operation_logs(self, hours: int = 24, 
                                 limit: int = 100) -> List[OperationLog]:
        """
        获取最近的操作日志
        
        Args:
            hours: 时间范围（小时）
            limit: 返回记录数限制
            
        Returns:
            List[OperationLog]: 操作日志列表
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            with get_db_session() as session:
                logs = session.query(OperationLog).filter(
                    OperationLog.created_at >= cutoff_time
                ).order_by(
                    OperationLog.created_at.desc()
                ).limit(limit).all()
                
                return logs
                
        except Exception as e:
            logger.error(f"获取最近操作日志失败: {e}")
            return []
    
    def search_operation_logs(self, query: str, 
                             page: int = 1, 
                             per_page: int = 50) -> Tuple[List[OperationLog], int]:
        """
        搜索操作日志
        
        Args:
            query: 搜索关键词
            page: 页码
            per_page: 每页数量
            
        Returns:
            Tuple[List[OperationLog], int]: (操作日志列表, 总数量)
        """
        try:
            with get_db_session() as session:
                search_filter = or_(
                    OperationLog.operation.ilike(f'%{query}%'),
                    OperationLog.resource.ilike(f'%{query}%')
                )
                
                query_obj = session.query(OperationLog).filter(search_filter)
                
                # 获取总数
                total = query_obj.count()
                
                # 分页和排序
                offset = (page - 1) * per_page
                logs = query_obj.order_by(OperationLog.created_at.desc()).offset(offset).limit(per_page).all()
                
                return logs, total
                
        except Exception as e:
            logger.error(f"搜索操作日志失败: {e}")
            return [], 0
    
    def get_operation_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        获取操作统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
            
            with get_db_session() as session:
                # 总操作次数
                total_operations = session.query(OperationLog).filter(
                    OperationLog.created_at >= cutoff_time
                ).count()
                
                # 各操作类型统计
                operation_counts = {}
                operations = session.query(OperationLog.operation, func.count(OperationLog.id)).filter(
                    OperationLog.created_at >= cutoff_time
                ).group_by(OperationLog.operation).all()
                
                for operation, count in operations:
                    operation_counts[operation] = count
                
                # 各资源统计
                resource_counts = {}
                resources = session.query(OperationLog.resource, func.count(OperationLog.id)).filter(
                    OperationLog.created_at >= cutoff_time
                ).group_by(OperationLog.resource).all()
                
                for resource, count in resources:
                    resource_counts[resource] = count
                
                # 活跃用户数
                active_users = session.query(OperationLog.user_id).filter(
                    and_(
                        OperationLog.user_id.isnot(None),
                        OperationLog.created_at >= cutoff_time
                    )
                ).distinct().count()
                
                return {
                    'period_days': days,
                    'total_operations': total_operations,
                    'operation_distribution': operation_counts,
                    'resource_distribution': resource_counts,
                    'active_users': active_users
                }
                
        except Exception as e:
            logger.error(f"获取操作统计失败: {e}")
            return {}
    
    # ============================================================================
    # 综合日志查询
    # ============================================================================
    
    def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        获取用户活动摘要
        
        Args:
            user_id: 用户ID
            days: 统计天数
            
        Returns:
            Dict[str, Any]: 用户活动摘要
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
            
            with get_db_session() as session:
                # 登录统计
                login_count = session.query(LoginLog).filter(
                    and_(
                        LoginLog.user_id == user_id,
                        LoginLog.login_time >= cutoff_time
                    )
                ).count()
                
                successful_logins = session.query(LoginLog).filter(
                    and_(
                        LoginLog.user_id == user_id,
                        LoginLog.status == 'success',
                        LoginLog.login_time >= cutoff_time
                    )
                ).count()
                
                # 操作统计
                operation_count = session.query(OperationLog).filter(
                    and_(
                        OperationLog.user_id == user_id,
                        OperationLog.created_at >= cutoff_time
                    )
                ).count()
                
                # 最后登录时间
                last_login = session.query(LoginLog).filter(
                    and_(
                        LoginLog.user_id == user_id,
                        LoginLog.status == 'success'
                    )
                ).order_by(LoginLog.login_time.desc()).first()
                
                # 最后操作时间
                last_operation = session.query(OperationLog).filter(
                    OperationLog.user_id == user_id
                ).order_by(OperationLog.created_at.desc()).first()
                
                return {
                    'user_id': user_id,
                    'period_days': days,
                    'login_count': login_count,
                    'successful_logins': successful_logins,
                    'operation_count': operation_count,
                    'last_login': last_login.login_time.isoformat() if last_login else None,
                    'last_operation': last_operation.created_at.isoformat() if last_operation else None
                }
                
        except Exception as e:
            logger.error(f"获取用户活动摘要失败: {e}")
            return {}
    
    def cleanup_old_logs(self, login_days: int = 90, operation_days: int = 365) -> Dict[str, int]:
        """
        清理旧日志
        
        Args:
            login_days: 保留登录日志的天数
            operation_days: 保留操作日志的天数
            
        Returns:
            Dict[str, int]: 清理结果统计
        """
        try:
            login_cutoff = datetime.now(timezone.utc) - timedelta(days=login_days)
            operation_cutoff = datetime.now(timezone.utc) - timedelta(days=operation_days)
            
            with get_db_session() as session:
                # 清理登录日志
                deleted_login_logs = session.query(LoginLog).filter(
                    LoginLog.login_time < login_cutoff
                ).delete()
                
                # 清理操作日志
                deleted_operation_logs = session.query(OperationLog).filter(
                    OperationLog.created_at < operation_cutoff
                ).delete()
                
                session.commit()
                
                result = {
                    'deleted_login_logs': deleted_login_logs,
                    'deleted_operation_logs': deleted_operation_logs
                }
                
                logger.info(f"日志清理完成: {result}")
                return result
                
        except Exception as e:
            logger.error(f"日志清理失败: {e}")
            raise DatabaseError(f"日志清理失败: {str(e)}")


# 创建全局日志服务实例
log_service = LogService()