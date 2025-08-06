"""
用户认证服务

提供用户登录、登出、令牌管理等认证相关功能
"""

import jwt
import redis
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from flask import current_app
from app.models.user import User
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.utils import generate_secure_token, verify_password
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        """初始化认证服务"""
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """初始化Redis连接"""
        try:
            from app.core.extensions import redis_client
            self.redis_client = redis_client
            logger.info("认证服务Redis连接初始化成功")
        except Exception as e:
            logger.warning(f"认证服务Redis连接初始化失败: {e}")
            self.redis_client = None
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """
        用户认证
        
        Args:
            username: 用户名或邮箱
            password: 密码
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串
            
        Returns:
            包含用户信息和令牌的字典
            
        Raises:
            AuthenticationError: 认证失败
        """
        logger.info(f"用户认证请求: {username}, IP: {ip_address}")
        
        try:
            # 查找用户
            user = self._find_user(username)
            if not user:
                self._log_failed_login(None, username, "用户不存在", ip_address, user_agent)
                raise AuthenticationError("用户名或密码错误")
            
            # 检查账户状态
            if not user.is_active:
                self._log_failed_login(user.id, username, "账户已禁用", ip_address, user_agent)
                raise AuthenticationError("账户已被禁用")
            
            # 检查登录失败次数
            if self._is_account_locked(user.id, ip_address):
                self._log_failed_login(user.id, username, "账户已锁定", ip_address, user_agent)
                raise AuthenticationError("账户已被锁定，请稍后再试")
            
            # 验证密码
            if not user.check_password(password):
                self._increment_failed_attempts(user.id, ip_address)
                self._log_failed_login(user.id, username, "密码错误", ip_address, user_agent)
                raise AuthenticationError("用户名或密码错误")
            
            # 认证成功，清除失败记录
            self._clear_failed_attempts(user.id, ip_address)
            
            # 生成JWT令牌
            access_token, refresh_token = self._generate_tokens(user)
            
            # 创建会话
            session_id = self._create_session(user, access_token, ip_address, user_agent)
            
            # 记录成功登录日志
            login_log = self._log_successful_login(user.id, username, ip_address, user_agent, session_id)
            
            # 记录操作日志
            from app.services.log_service import log_service
            log_service.create_operation_log(
                user_id=user.id,
                operation="login",
                resource="system",
                details={
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "session_id": session_id
                },
                ip_address=ip_address
            )
            
            # 更新用户最后登录时间
            user.last_login = datetime.now(timezone.utc)
            user.save()
            
            logger.info(f"用户 {username} 认证成功")
            
            # 获取过期时间（秒数）
            expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
            if isinstance(expires_in, timedelta):
                expires_in = int(expires_in.total_seconds())
            
            return {
                "user": user.to_dict(exclude_fields=['password_hash']),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "session_id": session_id,
                "expires_in": expires_in
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"用户认证异常: {e}")
            raise AuthenticationError("认证服务异常")
    
    def logout_user(self, user_id: str, session_id: str = None, 
                   ip_address: str = None) -> bool:
        """
        用户登出
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            ip_address: 客户端IP地址
            
        Returns:
            是否成功登出
        """
        logger.info(f"用户登出请求: {user_id}, 会话: {session_id}")
        
        try:
            # 获取用户信息
            from app.services.user_service import user_service
            user = user_service.get_user_by_id(user_id)
            if not user:
                logger.warning(f"登出时用户不存在: {user_id}")
                return False
            
            # 删除会话
            if session_id:
                self._delete_session(session_id)
            
            # 删除用户所有会话（可选）
            # self._delete_user_sessions(user_id)
            
            # 更新登录日志
            self._update_login_log_logout(user_id, session_id)
            
            # 记录操作日志
            from app.services.log_service import log_service
            log_service.create_operation_log(
                user_id=user_id,
                operation="logout",
                resource="system",
                details={
                    "session_id": session_id,
                    "ip_address": ip_address
                },
                ip_address=ip_address
            )
            
            logger.info(f"用户 {user.username} 登出成功")
            return True
            
        except Exception as e:
            logger.error(f"用户登出异常: {e}")
            return False
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            令牌载荷或None
        """
        try:
            # 解码JWT令牌
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # 检查令牌类型
            if payload.get('type') != 'access':
                logger.warning("无效的令牌类型")
                return None
            
            # 检查会话状态
            session_id = payload.get('session_id')
            if session_id and not self._is_session_valid(session_id):
                logger.warning(f"会话已失效: {session_id}")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效令牌: {e}")
            return None
        except Exception as e:
            logger.error(f"令牌验证异常: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的令牌对或None
        """
        try:
            # 解码刷新令牌
            payload = jwt.decode(
                refresh_token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # 检查令牌类型
            if payload.get('type') != 'refresh':
                logger.warning("无效的刷新令牌类型")
                return None
            
            # 获取用户信息
            user_id = payload.get('user_id')
            from app.services.user_service import user_service
            user = user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                logger.warning(f"刷新令牌对应的用户无效: {user_id}")
                return None
            
            # 检查会话状态
            session_id = payload.get('session_id')
            if session_id and not self._is_session_valid(session_id):
                logger.warning(f"刷新令牌对应的会话已失效: {session_id}")
                return None
            
            # 生成新的访问令牌
            access_token, new_refresh_token = self._generate_tokens(user, session_id)
            
            logger.info(f"用户 {user.username} 令牌刷新成功")
            
            # 获取过期时间（秒数）
            expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
            if isinstance(expires_in, timedelta):
                expires_in = int(expires_in.total_seconds())
            
            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "expires_in": expires_in
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("刷新令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效刷新令牌: {e}")
            return None
        except Exception as e:
            logger.error(f"令牌刷新异常: {e}")
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """
        根据令牌获取当前用户
        
        Args:
            token: JWT令牌
            
        Returns:
            用户对象或None
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        from app.services.user_service import user_service
        return user_service.get_user_by_id(user_id)
    
    def _find_user(self, username: str) -> Optional[User]:
        """查找用户（支持用户名和邮箱）"""
        from app.services.user_service import user_service
        # 先尝试用户名查找
        user = user_service.get_user_by_username(username)
        if user:
            return user
        
        # 再尝试邮箱查找
        user = user_service.get_user_by_email(username)
        return user
    
    def _generate_tokens(self, user: User, session_id: str = None) -> Tuple[str, str]:
        """生成JWT令牌对"""
        now = datetime.now(timezone.utc)
        
        # 如果没有提供session_id，生成新的
        if not session_id:
            session_id = generate_secure_token()
        
        # 获取令牌过期时间
        access_expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
        refresh_expires = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', 86400)
        
        # 如果配置是timedelta对象，转换为秒数
        if isinstance(access_expires, timedelta):
            access_expires = int(access_expires.total_seconds())
        if isinstance(refresh_expires, timedelta):
            refresh_expires = int(refresh_expires.total_seconds())
        
        # 访问令牌载荷
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'session_id': session_id,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(seconds=access_expires)
        }
        
        # 刷新令牌载荷
        refresh_payload = {
            'user_id': user.id,
            'session_id': session_id,
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(seconds=refresh_expires)
        }
        
        # 生成令牌
        access_token = jwt.encode(access_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return access_token, refresh_token
    
    def _create_session(self, user: User, access_token: str, 
                       ip_address: str = None, user_agent: str = None) -> str:
        """创建用户会话"""
        session_id = generate_secure_token()
        
        if self.redis_client:
            try:
                session_data = {
                    'user_id': user.id,
                    'username': user.username,
                    'ip_address': ip_address or '',
                    'user_agent': user_agent or '',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'last_activity': datetime.now(timezone.utc).isoformat()
                }
                
                # 存储会话信息，设置过期时间
                session_key = f"session:{session_id}"
                self.redis_client.hmset(session_key, session_data)
                self.redis_client.expire(session_key, current_app.config.get('SESSION_TIMEOUT', 86400))
                
                # 存储用户活跃会话列表
                user_sessions_key = f"user_sessions:{user.id}"
                self.redis_client.sadd(user_sessions_key, session_id)
                self.redis_client.expire(user_sessions_key, current_app.config.get('SESSION_TIMEOUT', 86400))
                
                logger.debug(f"会话创建成功: {session_id}")
                
            except Exception as e:
                logger.warning(f"Redis会话存储失败: {e}")
        
        return session_id
    
    def _delete_session(self, session_id: str):
        """删除会话"""
        if self.redis_client:
            try:
                session_key = f"session:{session_id}"
                session_data = self.redis_client.hgetall(session_key)
                
                if session_data:
                    user_id = session_data.get('user_id')
                    if user_id:
                        # 从用户会话列表中移除
                        user_sessions_key = f"user_sessions:{user_id}"
                        self.redis_client.srem(user_sessions_key, session_id)
                    
                    # 删除会话数据
                    self.redis_client.delete(session_key)
                    logger.debug(f"会话删除成功: {session_id}")
                
            except Exception as e:
                logger.warning(f"Redis会话删除失败: {e}")
    
    def _is_session_valid(self, session_id: str) -> bool:
        """检查会话是否有效"""
        if not self.redis_client:
            return True  # 如果没有Redis，跳过会话检查
        
        try:
            session_key = f"session:{session_id}"
            exists = self.redis_client.exists(session_key)
            
            if exists:
                # 更新最后活动时间
                self.redis_client.hset(session_key, 'last_activity', 
                                     datetime.now(timezone.utc).isoformat())
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"会话检查失败: {e}")
            return True  # 出错时允许通过
    
    def _is_account_locked(self, user_id: str, ip_address: str = None) -> bool:
        """检查账户是否被锁定"""
        if not self.redis_client:
            return False
        
        try:
            max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
            lockout_duration = current_app.config.get('LOCKOUT_DURATION', 900)  # 15分钟
            
            # 检查用户级别的失败次数
            user_key = f"failed_attempts:user:{user_id}"
            user_attempts = int(self.redis_client.get(user_key) or 0)
            
            # 检查IP级别的失败次数
            ip_attempts = 0
            if ip_address:
                ip_key = f"failed_attempts:ip:{ip_address}"
                ip_attempts = int(self.redis_client.get(ip_key) or 0)
            
            return user_attempts >= max_attempts or ip_attempts >= max_attempts
            
        except Exception as e:
            logger.warning(f"账户锁定检查失败: {e}")
            return False
    
    def _increment_failed_attempts(self, user_id: str, ip_address: str = None):
        """增加失败尝试次数"""
        if not self.redis_client:
            return
        
        try:
            lockout_duration = current_app.config.get('LOCKOUT_DURATION', 900)
            
            # 增加用户级别的失败次数
            user_key = f"failed_attempts:user:{user_id}"
            self.redis_client.incr(user_key)
            self.redis_client.expire(user_key, lockout_duration)
            
            # 增加IP级别的失败次数
            if ip_address:
                ip_key = f"failed_attempts:ip:{ip_address}"
                self.redis_client.incr(ip_key)
                self.redis_client.expire(ip_key, lockout_duration)
            
        except Exception as e:
            logger.warning(f"失败次数记录失败: {e}")
    
    def _clear_failed_attempts(self, user_id: str, ip_address: str = None):
        """清除失败尝试记录"""
        if not self.redis_client:
            return
        
        try:
            # 清除用户级别的失败次数
            user_key = f"failed_attempts:user:{user_id}"
            self.redis_client.delete(user_key)
            
            # 清除IP级别的失败次数
            if ip_address:
                ip_key = f"failed_attempts:ip:{ip_address}"
                self.redis_client.delete(ip_key)
            
        except Exception as e:
            logger.warning(f"失败次数清除失败: {e}")
    
    def _log_successful_login(self, user_id: str, username: str, 
                            ip_address: str = None, user_agent: str = None,
                            session_id: str = None):
        """记录成功登录日志"""
        from app.services.log_service import log_service
        return log_service.create_login_log(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status="success"
        )
    
    def _log_failed_login(self, user_id: str, username: str, reason: str,
                         ip_address: str = None, user_agent: str = None):
        """记录失败登录日志"""
        from app.services.log_service import log_service
        log_service.create_login_log(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status="failed"
        )
    
    def _update_login_log_logout(self, user_id: str, session_id: str = None):
        """更新登录日志的登出时间"""
        try:
            from app.services.log_service import log_service
            # 查找最近的成功登录日志
            recent_logs, _ = log_service.get_login_logs_by_user(user_id, page=1, per_page=10)
            for log in recent_logs:
                if log.status == "success" and log.logout_time is None:
                    log_service.update_logout_time(log.id)
                    break
        except Exception as e:
            logger.warning(f"更新登录日志失败: {e}")


# 全局认证服务实例
auth_service = AuthService()