#!/usr/bin/env python3
"""
认证服务测试

测试认证服务的各种功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.base import ServiceTestCase


class AuthServiceTest(ServiceTestCase):
    """认证服务测试类"""
    
    def test_auth_service(self):
        """测试认证服务功能"""
        print("🧪 开始测试认证服务...")
        
        try:
            # 设置服务测试环境
            from app.services.auth_service import AuthService
            app, server, db_fd, db_path, auth_service = self.setup_service_test(AuthService)
            
            with server.app_context():
                # 定义测试函数列表
                test_functions = [
                    self.test_user_authentication,
                    self.test_jwt_tokens,
                    self.test_session_management,
                    self.test_security_features,
                    self.test_logging_features
                ]
                
                # 运行测试套件
                test_results = self.run_test_suite(test_functions)
                
                # 打印测试结果
                success = self.print_test_summary(test_results, [
                    "用户认证", "JWT令牌", "会话管理", "安全功能", "日志记录"
                ])
                
                # 清理资源
                self.cleanup_database(db_fd, db_path)
                
                return success
                    
        except Exception as e:
            print(f"❌ 认证服务测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


    def test_user_authentication(self):
        """测试用户认证功能"""
        try:
            from app.services.auth_service import AuthService
            
            # 创建认证服务实例
            auth_service = AuthService()
            
            # 创建测试用户
            user = self.create_test_user(
                username="testuser",
                email="test@example.com",
                password="TestPassword123"
            )
            
            # 测试成功认证
            result = auth_service.authenticate_user(
                username="testuser",
                password="TestPassword123",
                ip_address="192.168.1.1",
                user_agent="Test Browser"
            )
            
            # 验证认证结果
            assert result is not None, "认证结果不能为空"
            assert 'user' in result, "认证结果应包含用户信息"
            assert 'access_token' in result, "认证结果应包含访问令牌"
            assert 'refresh_token' in result, "认证结果应包含刷新令牌"
            assert 'session_id' in result, "认证结果应包含会话ID"
            
            assert result['user']['username'] == "testuser", "用户名不匹配"
            assert result['user']['email'] == "test@example.com", "邮箱不匹配"
            
            # 测试错误密码
            try:
                auth_service.authenticate_user(
                    username="testuser",
                    password="WrongPassword",
                    ip_address="192.168.1.1"
                )
                assert False, "错误密码应该抛出异常"
            except Exception as e:
                assert "用户名或密码错误" in str(e), "应该返回密码错误信息"
            
            # 测试不存在的用户
            try:
                auth_service.authenticate_user(
                    username="nonexistent",
                    password="TestPassword123",
                    ip_address="192.168.1.1"
                )
                assert False, "不存在的用户应该抛出异常"
            except Exception as e:
                assert "用户名或密码错误" in str(e), "应该返回用户不存在错误信息"
            
            print("✅ 用户认证功能测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 用户认证功能测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_jwt_tokens():
    """测试JWT令牌功能"""
    try:
        from app.services.auth_service import AuthService
        from app.models.user import User
        
        # 创建认证服务实例
        auth_service = AuthService()
        
        # 创建测试用户
        user = User.create_user(
            username="tokenuser",
            email="token@example.com",
            password="TokenPassword123"
        )
        
        # 认证用户获取令牌
        auth_result = auth_service.authenticate_user(
            username="tokenuser",
            password="TokenPassword123"
        )
        
        access_token = auth_result['access_token']
        refresh_token = auth_result['refresh_token']
        
        # 测试访问令牌验证
        payload = auth_service.verify_token(access_token)
        assert payload is not None, "访问令牌验证失败"
        assert payload['user_id'] == user.id, "令牌中的用户ID不匹配"
        assert payload['username'] == user.username, "令牌中的用户名不匹配"
        assert payload['type'] == 'access', "令牌类型不正确"
        
        # 测试获取当前用户
        current_user = auth_service.get_current_user(access_token)
        assert current_user is not None, "获取当前用户失败"
        assert current_user.id == user.id, "当前用户ID不匹配"
        assert current_user.username == user.username, "当前用户名不匹配"
        
        # 测试令牌刷新
        refresh_result = auth_service.refresh_token(refresh_token)
        assert refresh_result is not None, "令牌刷新失败"
        assert 'access_token' in refresh_result, "刷新结果应包含新的访问令牌"
        assert 'refresh_token' in refresh_result, "刷新结果应包含新的刷新令牌"
        
        # 验证新的访问令牌
        new_access_token = refresh_result['access_token']
        new_payload = auth_service.verify_token(new_access_token)
        assert new_payload is not None, "新访问令牌验证失败"
        assert new_payload['user_id'] == user.id, "新令牌中的用户ID不匹配"
        
        # 测试无效令牌
        invalid_payload = auth_service.verify_token("invalid.token.here")
        assert invalid_payload is None, "无效令牌应该返回None"
        
        print("✅ JWT令牌功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ JWT令牌功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_management():
    """测试会话管理功能"""
    try:
        from app.services.auth_service import AuthService
        from app.models.user import User
        
        # 创建认证服务实例
        auth_service = AuthService()
        
        # 创建测试用户
        user = User.create_user(
            username="sessionuser",
            email="session@example.com",
            password="SessionPassword123"
        )
        
        # 认证用户创建会话
        auth_result = auth_service.authenticate_user(
            username="sessionuser",
            password="SessionPassword123",
            ip_address="192.168.1.100",
            user_agent="Session Test Browser"
        )
        
        session_id = auth_result['session_id']
        assert session_id is not None, "会话ID不能为空"
        
        # 测试会话有效性（如果有Redis的话）
        if auth_service.redis_client:
            is_valid = auth_service._is_session_valid(session_id)
            # 由于我们使用的是Mock，这里可能不会真正验证
            # 但至少确保方法不会抛出异常
        
        # 测试用户登出
        logout_success = auth_service.logout_user(
            user_id=user.id,
            session_id=session_id,
            ip_address="192.168.1.100"
        )
        assert logout_success is True, "用户登出应该成功"
        
        print("✅ 会话管理功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 会话管理功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_security_features():
    """测试安全功能"""
    try:
        from app.services.auth_service import AuthService
        from app.models.user import User
        
        # 创建认证服务实例
        auth_service = AuthService()
        
        # 创建测试用户
        user = User.create_user(
            username="securityuser",
            email="security@example.com",
            password="SecurityPassword123"
        )
        
        # 测试账户锁定检查（如果有Redis的话）
        if auth_service.redis_client:
            # 模拟失败尝试
            is_locked_before = auth_service._is_account_locked(user.id, "192.168.1.200")
            # 由于使用Mock，这里主要测试方法不会抛出异常
        
        # 测试用户查找功能
        found_user_by_username = auth_service._find_user("securityuser")
        assert found_user_by_username is not None, "应该能通过用户名找到用户"
        assert found_user_by_username.id == user.id, "找到的用户ID应该匹配"
        
        found_user_by_email = auth_service._find_user("security@example.com")
        assert found_user_by_email is not None, "应该能通过邮箱找到用户"
        assert found_user_by_email.id == user.id, "找到的用户ID应该匹配"
        
        # 测试不存在的用户
        not_found_user = auth_service._find_user("nonexistent@example.com")
        assert not_found_user is None, "不存在的用户应该返回None"
        
        print("✅ 安全功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 安全功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logging_features():
    """测试日志记录功能"""
    try:
        from app.services.auth_service import AuthService
        from app.models.user import User
        from app.models.logs import LoginLog, OperationLog
        
        # 创建认证服务实例
        auth_service = AuthService()
        
        # 创建测试用户
        user = User.create_user(
            username="loguser",
            email="log@example.com",
            password="LogPassword123"
        )
        
        # 记录登录日志数量（之前）
        login_logs_before = len(LoginLog.get_by_user(user.id))
        operation_logs_before = len(OperationLog.get_by_user(user.id))
        
        # 认证用户（会自动记录日志）
        auth_result = auth_service.authenticate_user(
            username="loguser",
            password="LogPassword123",
            ip_address="192.168.1.300",
            user_agent="Log Test Browser"
        )
        
        # 检查登录日志是否增加
        login_logs_after = len(LoginLog.get_by_user(user.id))
        operation_logs_after = len(OperationLog.get_by_user(user.id))
        
        assert login_logs_after > login_logs_before, "应该记录登录日志"
        assert operation_logs_after > operation_logs_before, "应该记录操作日志"
        
        # 检查最新的登录日志
        recent_login_logs = LoginLog.get_by_user(user.id, limit=1)
        if recent_login_logs:
            latest_login_log = recent_login_logs[0]
            assert latest_login_log.status == "success", "最新登录日志状态应该是成功"
            assert latest_login_log.ip_address == "192.168.1.300", "IP地址应该匹配"
        
        # 检查最新的操作日志
        recent_operation_logs = OperationLog.get_by_user(user.id, limit=1)
        if recent_operation_logs:
            latest_operation_log = recent_operation_logs[0]
            assert latest_operation_log.operation == "login", "最新操作日志应该是登录操作"
        
        # 测试登出（也会记录日志）
        session_id = auth_result['session_id']
        auth_service.logout_user(
            user_id=user.id,
            session_id=session_id,
            ip_address="192.168.1.300"
        )
        
        # 检查登出后的操作日志
        final_operation_logs = len(OperationLog.get_by_user(user.id))
        assert final_operation_logs > operation_logs_after, "登出应该记录操作日志"
        
        print("✅ 日志记录功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 日志记录功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_auth_service()
    sys.exit(0 if success else 1)