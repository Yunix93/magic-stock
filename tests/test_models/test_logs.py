#!/usr/bin/env python3
"""
日志记录模型测试

测试登录日志和操作日志模型的各种功能
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_logs_model():
    """测试日志模型基本功能"""
    print("🧪 开始测试日志模型...")
    
    try:
        # 使用统一的配置管理
        from app.core.config_manager import config_manager
        
        # 创建应用实例，使用真实的SQLite数据库
        from app import create_app
        app, server = create_app('testing')
        
        # 使用临时数据库文件而不是内存数据库
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        
        with server.app_context():
            # 初始化数据库
            from app.models.base import init_database, create_tables
            database_url = server.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"  使用数据库: {database_url}")
            engine, session = init_database(database_url)
            
            # 使用统一的模型导入
            from app.models import User, Role, Permission, LoginLog, OperationLog, UserRole, RolePermission
            
            create_tables()
            
            # 测试日志模型
            test_results = []
            
            # 1. 测试登录日志模型
            print("\n📝 测试登录日志模型...")
            test_results.append(test_login_log_model())
            
            # 2. 测试操作日志模型
            print("\n🔐 测试操作日志模型...")
            test_results.append(test_operation_log_model())
            
            # 输出测试结果
            passed = sum(test_results)
            total = len(test_results)
            
            print(f"\n📋 测试结果汇总:")
            print(f"  通过: {passed}/{total}")
            
            if passed == total:
                print("🎉 所有日志模型测试通过！")
                result = True
            else:
                print("❌ 部分测试失败")
                result = False
        
            # 清理临时数据库文件
            try:
                os.close(db_fd)
                os.unlink(db_path)
            except:
                pass
            
            return result
                
    except Exception as e:
        print(f"❌ 日志模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_login_log_model():
    """测试登录日志模型"""
    try:
        from app.models.logs import LoginLog
        from app.models.user import User
        
        # 创建测试用户
        user = User.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123"
        )
        
        # 创建登录日志
        login_log = LoginLog.create_login_log(
            user_id=user.id,
            ip_address="192.168.1.1",
            user_agent="Test Browser",
            status="success"
        )
        
        # 验证基本属性
        assert login_log.user_id == user.id
        assert login_log.ip_address == "192.168.1.1"
        assert login_log.user_agent == "Test Browser"
        assert login_log.status == "success"
        assert login_log.login_time is not None
        assert login_log.logout_time is None
        
        # 测试设置登出时间
        login_log.set_logout()
        assert login_log.logout_time is not None
        
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


def test_operation_log_model():
    """测试操作日志模型"""
    try:
        from app.models.logs import OperationLog
        from app.models.user import User
        
        # 创建测试用户
        user = User.create_user(
            username="testuser2",
            email="test2@example.com",
            password="TestPassword123"
        )
        
        # 创建操作日志
        operation_log = OperationLog.create_operation_log(
            user_id=user.id,
            operation="create_user",
            resource="user",
            details={"username": "newuser", "email": "new@example.com"},
            ip_address="192.168.1.2"
        )
        
        # 验证基本属性
        assert operation_log.user_id == user.id
        assert operation_log.operation == "create_user"
        assert operation_log.resource == "user"
        assert operation_log.ip_address == "192.168.1.2"
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


def main():
    """主测试函数"""
    print("🚀 开始日志模型测试...")
    
    success = test_logs_model()
    
    if success:
        print("\n🎉 日志模型测试全部通过！")
        return True
    else:
        print("\n❌ 日志模型测试失败，请检查代码。")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)


class TestLoginLogModel:
    """登录日志模型测试类"""
    
    def test_login_log_creation(self, db_session):
        """测试登录日志创建"""
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
        # 测试无效状态
        with pytest.raises(ValidationError):
            LoginLog(status="invalid_status")
    
    def test_set_logout(self, db_session):
        """测试设置登出时间"""
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
    """操作日志模型测试类"""
    
    def test_operation_log_creation(self, db_session):
        """测试操作日志创建"""
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
        # 测试操作类型验证
        with pytest.raises(ValidationError):
            OperationLog(operation="", resource="user")
        
        # 测试资源验证
        with pytest.raises(ValidationError):
            OperationLog(operation="create", resource="")
    
    def test_details_handling(self, db_session):
        """测试详情数据处理"""
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
        
        # 测试必要参数验证
        with pytest.raises(ValidationError):
            OperationLog.create_operation_log(operation=None, resource="user")
        
        with pytest.raises(ValidationError):
            OperationLog.create_operation_log(operation="create", resource=None)
    
    def test_get_by_resource(self, db_session):
        """测试根据资源获取日志"""
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
    """日志集成测试"""
    
    def test_user_login_logout_flow(self, db_session):
        """测试用户登录登出流程"""
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