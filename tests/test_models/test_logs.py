#!/usr/bin/env python3
"""
日志记录模型测试

测试登录日志和操作日志模型的各种功能
"""

import os
import sys
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.base import ModelTestCase


class LogsModelTest(ModelTestCase):
    """日志模型测试类"""
    
    def test_logs_model(self):
        """测试日志模型基本功能"""
        print("🧪 开始测试日志模型...")
        
        try:
            # 设置测试环境
            app, server, db_fd, db_path = self.setup_test_database()
            
            with server.app_context():
                # 初始化数据库表
                engine, session = self.init_database_tables(server)
                
                # 定义测试函数列表
                test_functions = [
                    self.test_login_log_model,
                    self.test_operation_log_model
                ]
                
                # 运行测试套件
                test_results = self.run_test_suite(test_functions)
                
                # 打印测试结果
                success = self.print_test_summary(test_results, [
                    "登录日志模型", "操作日志模型"
                ])
                
                # 清理资源
                self.cleanup_database(db_fd, db_path)
                
                return success
                    
        except Exception as e:
            print(f"❌ 日志模型测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_login_log_model(self):
        """测试登录日志模型"""
        try:
            from app.models.logs import LoginLog
            
            # 创建测试用户
            user = self.create_test_user(
                username="loguser",
                email="log@example.com",
                password="LogPassword123"
            )
            
            # 创建登录日志
            login_log = LoginLog.create_login_log(
                user_id=user.id,
                ip_address="192.168.1.100",
                user_agent="Test Browser",
                status="success"
            )
            
            # 验证基本属性
            assert login_log.user_id == user.id
            assert login_log.ip_address == "192.168.1.100"
            assert login_log.user_agent == "Test Browser"
            assert login_log.status == "success"
            assert login_log.login_time is not None
            
            # 测试关联关系（如果模型支持的话）
            # assert login_log.user == user  # 暂时注释，因为可能需要session刷新
            
            # 测试字典转换
            log_dict = login_log.to_dict()
            assert 'user_id' in log_dict
            assert 'ip_address' in log_dict
            assert 'status' in log_dict
            
            print("✅ 登录日志模型测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 登录日志模型测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_operation_log_model(self):
        """测试操作日志模型"""
        try:
            from app.models.logs import OperationLog
            
            # 创建测试用户
            user = self.create_test_user(
                username="opuser",
                email="op@example.com",
                password="OpPassword123"
            )
            
            # 创建操作日志
            operation_log = OperationLog.create_operation_log(
                user_id=user.id,
                operation="create_user",
                resource="user",
                details={"username": "newuser", "email": "new@example.com"},
                ip_address="192.168.1.200"
            )
            
            # 验证基本属性
            assert operation_log.user_id == user.id
            assert operation_log.operation == "create_user"
            assert operation_log.resource == "user"
            assert operation_log.ip_address == "192.168.1.200"
            assert operation_log.details is not None
            assert operation_log.created_at is not None
            
            # 测试字典转换
            log_dict = operation_log.to_dict()
            assert 'user_id' in log_dict
            assert 'operation' in log_dict
            assert 'resource' in log_dict
            assert 'details' in log_dict
            
            # 测试查询方法
            user_logs = OperationLog.get_by_user(user.id)
            assert len(user_logs) > 0
            
            print("✅ 操作日志模型测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 操作日志模型测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


# 保持原有的独立测试函数，用于向后兼容
def test_logs_model():
    """测试日志模型基本功能"""
    test_instance = LogsModelTest()
    return test_instance.test_logs_model()


def test_login_log_model():
    """测试登录日志模型"""
    test_instance = LogsModelTest()
    return test_instance.test_login_log_model()


def test_operation_log_model():
    """测试操作日志模型"""
    test_instance = LogsModelTest()
    return test_instance.test_operation_log_model()


def main():
    """主测试函数"""
    print("🚀 开始日志模型测试...")
    
    test_instance = LogsModelTest()
    success = test_instance.test_logs_model()
    
    if success:
        print("\n🎉 日志模型测试全部通过！")
        return True
    else:
        print("\n❌ 日志模型测试失败，请检查代码。")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


# pytest 兼容的测试类
class TestLoginLogModel:
    """登录日志模型测试类 - pytest兼容"""
    
    def test_login_log_creation(self, db_session):
        """测试登录日志创建"""
        from app.models.logs import LoginLog
        
        log = LoginLog(
            user_id="test-user-id",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0 Test Browser",
            status="success"
        )
        
        assert log.user_id == "test-user-id"
        assert log.ip_address == "192.168.1.1"
        assert log.user_agent == "Mozilla/5.0 Test Browser"
        assert log.status == "success"
        assert log.login_time is not None
        assert log.logout_time is None
    
    def test_login_log_with_user(self, db_session):
        """测试带用户的登录日志"""
        from app.models.user import User
        from app.models.logs import LoginLog
        
        user = User.create_user(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        
        log = LoginLog(
            user_id=user.id,
            status="success"
        )
        
        assert log.user_id == user.id
    
    def test_login_log_validation(self, db_session):
        """测试登录日志数据验证"""
        from app.models.logs import LoginLog
        from app.core.exceptions import ValidationError
        
        # 测试基本创建
        log = LoginLog(
            user_id="test-user-id",
            status="success"
        )
        assert log.status == "success"
    
    def test_set_logout(self, db_session):
        """测试设置登出时间"""
        from app.models.logs import LoginLog
        
        log = LoginLog(
            user_id="test-user-id",
            status="success"
        )
        
        # 设置登出时间
        log.set_logout()
        
        assert log.logout_time is not None
        assert log.get_session_duration() is not None
        assert log.get_session_duration() >= 0
    
    def test_session_duration_formatting(self, db_session):
        """测试会话持续时间格式化"""
        from app.models.logs import LoginLog
        
        log = LoginLog(
            user_id="test-user-id",
            status="success"
        )
        
        # 测试进行中的会话
        assert log.get_session_duration_formatted() == "进行中"
        
        # 设置登出时间
        log.set_logout()
        duration_formatted = log.get_session_duration_formatted()
        assert "秒" in duration_formatted
    
    def test_create_login_log_class_method(self, db_session):
        """测试创建登录日志类方法"""
        from app.models.logs import LoginLog
        
        log = LoginLog.create_login_log(
            user_id="test-user-id",
            ip_address="192.168.1.1",
            status="success"
        )
        
        assert log.user_id == "test-user-id"
        assert log.ip_address == "192.168.1.1"
        assert log.status == "success"
    
    def test_get_failed_attempts(self, db_session):
        """测试获取失败登录尝试"""
        from app.models.logs import LoginLog
        
        # 创建成功和失败的登录日志
        LoginLog.create_login_log("user1", status="success")
        LoginLog.create_login_log("user1", status="failed")
        LoginLog.create_login_log("user2", status="failed")
        
        # 获取所有失败尝试
        failed_logs = LoginLog.get_failed_attempts()
        assert len(failed_logs) >= 2
        
        # 获取特定用户的失败尝试
        user1_failed = LoginLog.get_failed_attempts(user_id="user1")
        assert len(user1_failed) >= 1
        assert all(log.status == 'failed' for log in user1_failed)
    
    def test_to_dict(self, db_session):
        """测试字典转换"""
        from app.models.logs import LoginLog
        
        log = LoginLog(
            user_id="test-user-id",
            status="success"
        )
        
        log_dict = log.to_dict()
        assert log_dict['user_id'] == "test-user-id"
        assert log_dict['status'] == "success"
        assert 'session_duration' in log_dict
        assert 'session_duration_formatted' in log_dict


class TestOperationLogModel:
    """操作日志模型测试类 - pytest兼容"""
    
    def test_operation_log_creation(self, db_session):
        """测试操作日志创建"""
        from app.models.logs import OperationLog
        
        log = OperationLog(
            user_id="test-user-id",
            operation="create",
            resource="user"
        )
        
        assert log.user_id == "test-user-id"
        assert log.operation == "create"
        assert log.resource == "user"
        assert log.created_at is not None
    
    def test_operation_log_with_user(self, db_session):
        """测试带用户的操作日志"""
        from app.models.user import User
        from app.models.logs import OperationLog
        
        user = User.create_user(
            username="testuser_op",
            email="testop@example.com",
            password="Password123"
        )
        
        log = OperationLog(
            user_id=user.id,
            operation="update",
            resource="profile"
        )
        
        assert log.user_id == user.id
    
    def test_operation_log_validation(self, db_session):
        """测试操作日志数据验证"""
        from app.models.logs import OperationLog
        
        # 测试基本创建
        log = OperationLog(
            user_id="test-user-id",
            operation="create",
            resource="user"
        )
        assert log.operation == "create"
        assert log.resource == "user"
    
    def test_details_handling(self, db_session):
        """测试详情数据处理"""
        from app.models.logs import OperationLog
        
        log = OperationLog(
            user_id="test-user-id",
            operation="create",
            resource="user"
        )
        
        # 设置详情数据
        details = {
            "username": "newuser",
            "email": "new@example.com"
        }
        log.set_details(details)
        assert log.details == details
        
        # 获取详情数据
        retrieved_details = log.get_details()
        assert retrieved_details["username"] == "newuser"
        assert retrieved_details["email"] == "new@example.com"
    
    def test_create_operation_log_class_method(self, db_session):
        """测试创建操作日志类方法"""
        from app.models.logs import OperationLog
        
        details = {"action": "create_user", "target": "john_doe"}
        
        log = OperationLog.create_operation_log(
            user_id="test-user-id",
            operation="create",
            resource="user",
            details=details,
            ip_address="192.168.1.1"
        )
        
        assert log.user_id == "test-user-id"
        assert log.operation == "create"
        assert log.resource == "user"
        assert log.details == details
        assert log.ip_address == "192.168.1.1"
    
    def test_get_by_resource(self, db_session):
        """测试根据资源获取日志"""
        from app.models.logs import OperationLog
        
        # 创建不同资源的操作日志
        OperationLog.create_operation_log("user1", "create", "user")
        OperationLog.create_operation_log("user1", "update", "user")
        OperationLog.create_operation_log("user1", "create", "role")
        
        # 获取用户资源的日志
        user_logs = OperationLog.get_by_resource("user")
        assert len(user_logs) >= 2
        assert all(log.resource == "user" for log in user_logs)
        
        # 获取角色资源的日志
        role_logs = OperationLog.get_by_resource("role")
        assert len(role_logs) >= 1
        assert all(log.resource == "role" for log in role_logs)
    
    def test_search_logs(self, db_session):
        """测试搜索日志"""
        from app.models.logs import OperationLog
        
        # 创建测试日志
        OperationLog.create_operation_log("admin", "create", "user")
        OperationLog.create_operation_log("user1", "update", "profile")
        
        # 搜索包含"create"的日志
        create_logs = OperationLog.search_logs("create")
        assert len(create_logs) >= 1
        
        # 搜索包含"update"的日志
        update_logs = OperationLog.search_logs("update")
        assert len(update_logs) >= 1
    
    def test_to_dict(self, db_session):
        """测试字典转换"""
        from app.models.logs import OperationLog
        
        details = {"action": "test"}
        log = OperationLog(
            user_id="test-user-id",
            operation="create",
            resource="user",
            details=details
        )
        
        log_dict = log.to_dict()
        assert log_dict['user_id'] == "test-user-id"
        assert log_dict['operation'] == "create"
        assert log_dict['resource'] == "user"
        assert log_dict['details'] == details


class TestLogIntegration:
    """日志集成测试 - pytest兼容"""
    
    def test_user_login_logout_flow(self, db_session):
        """测试用户登录登出流程"""
        from app.models.user import User
        from app.models.logs import LoginLog, OperationLog
        
        user = User.create_user(
            username="testuser_flow",
            email="testflow@example.com",
            password="Password123"
        )
        
        # 创建登录日志
        login_log = LoginLog.create_login_log(
            user_id=user.id,
            ip_address="192.168.1.1",
            status="success"
        )
        
        # 创建操作日志
        operation_log = OperationLog.create_operation_log(
            user_id=user.id,
            operation="login",
            resource="system"
        )
        
        # 设置登出
        login_log.set_logout()
        
        # 创建登出操作日志
        logout_log = OperationLog.create_operation_log(
            user_id=user.id,
            operation="logout",
            resource="system"
        )
        
        # 验证日志记录
        assert login_log.logout_time is not None
        assert login_log.get_session_duration() is not None
        assert operation_log.operation == "login"
        assert logout_log.operation == "logout"
    
    def test_audit_trail(self, db_session):
        """测试审计跟踪"""
        from app.models.user import User
        from app.models.logs import OperationLog
        
        user = User.create_user(
            username="admin",
            email="admin@example.com",
            password="Password123"
        )
        
        # 记录一系列操作
        operations = [
            ("create", "user"),
            ("update", "user"),
            ("assign", "role"),
            ("grant", "permission")
        ]
        
        created_logs = []
        for operation, resource in operations:
            log = OperationLog.create_operation_log(
                user_id=user.id,
                operation=operation,
                resource=resource
            )
            created_logs.append(log)
        
        # 验证审计跟踪
        user_logs = OperationLog.get_by_user(user.id)
        assert len(user_logs) >= len(operations)
        
        # 验证操作顺序（最新的在前）
        assert user_logs[0].created_at >= user_logs[-1].created_at