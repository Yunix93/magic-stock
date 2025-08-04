#!/usr/bin/env python3
"""
用户模型测试

测试用户模型的基本功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.base import ModelTestCase


class UserModelTest(ModelTestCase):
    """用户模型测试类"""
    
    def test_user_model(self):
        """测试用户模型基本功能"""
        print("🧪 开始测试用户模型...")
        
        try:
            # 设置测试环境
            app, server, db_fd, db_path = self.setup_test_database()
            
            with server.app_context():
                # 初始化数据库表
                engine, session = self.init_database_tables(server)
                
                # 定义测试函数列表
                test_functions = [
                    self.test_user_creation,
                    self.test_password_functionality,
                    self.test_user_authentication,
                    self.test_user_status_management,
                    self.test_data_validation
                ]
                
                # 运行测试套件
                test_results = self.run_test_suite(test_functions)
                
                # 打印测试结果
                success = self.print_test_summary(test_results, [
                    "用户创建", "密码功能", "用户认证", "状态管理", "数据验证"
                ])
                
                # 清理资源
                self.cleanup_database(db_fd, db_path)
                
                return success
                    
        except Exception as e:
            print(f"❌ 用户模型测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


    def test_user_creation(self):
        """测试用户创建"""
        try:
            # 使用基类的工厂方法创建用户
            user = self.create_test_user(
                username="testuser",
                email="test@example.com",
                password="TestPassword123",
                full_name="Test User"
            )
            
            # 验证基本属性
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.full_name == "Test User"
            assert user.password_hash is not None
            assert user.password_hash != "TestPassword123"
            assert user.is_active is True
            assert user.is_verified is False
            
            print("✅ 用户创建测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 用户创建测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


    def test_password_functionality(self):
        """测试密码功能"""
        try:
            user = self.create_test_user(
                username="testuser2",
                email="test2@example.com",
                password="TestPassword123"
            )
            
            # 测试密码验证
            assert user.check_password("TestPassword123") is True
            assert user.check_password("WrongPassword") is False
            
            # 测试密码修改
            old_hash = user.password_hash
            user.set_password("NewPassword123")
            assert user.password_hash != old_hash
            assert user.check_password("NewPassword123") is True
            assert user.check_password("TestPassword123") is False
            
            print("✅ 密码功能测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 密码功能测试失败: {e}")
            return False


    def test_user_authentication(self):
        """测试用户认证"""
        try:
            from app.core.exceptions import AuthenticationError
            
            user = self.create_test_user(
                username="testuser3",
                email="test3@example.com",
                password="TestPassword123"
            )
            
            # 测试成功认证
            assert user.authenticate("TestPassword123") is True
            assert user.last_login is not None
            
            # 测试失败认证
            try:
                user.authenticate("WrongPassword")
                assert False, "应该抛出认证异常"
            except AuthenticationError:
                pass
            
            # 测试停用用户认证
            user.deactivate()
            try:
                user.authenticate("TestPassword123")
                assert False, "停用用户应该无法认证"
            except AuthenticationError:
                pass
            
            print("✅ 用户认证测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 用户认证测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


    def test_user_status_management(self):
        """测试用户状态管理"""
        try:
            from app.core.constants import UserStatus
            
            user = self.create_test_user(
                username="testuser4",
                email="test4@example.com",
                password="TestPassword123"
            )
            
            # 测试初始状态
            assert user.get_status() == UserStatus.PENDING.value
            
            # 测试邮箱验证
            user.verify_email()
            assert user.get_status() == UserStatus.ACTIVE.value
            assert user.is_verified is True
            
            # 测试停用
            user.deactivate()
            assert user.get_status() == UserStatus.INACTIVE.value
            assert user.is_active is False
            
            # 测试激活
            user.activate()
            assert user.get_status() == UserStatus.ACTIVE.value
            assert user.is_active is True
            
            # 测试锁定
            user.lock_account(30)
            assert user.get_status() == UserStatus.SUSPENDED.value
            assert user.is_locked() is True
            
            print("✅ 用户状态管理测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 用户状态管理测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


    def test_data_validation(self):
        """测试数据验证"""
        try:
            from app.core.exceptions import ValidationError
            from app.models.user import User
            
            # 测试用户名验证
            try:
                User.create_user(username="ab", email="test@example.com", password="TestPassword123")
                assert False, "应该抛出验证异常"
            except ValidationError:
                pass
            
            # 测试邮箱验证
            try:
                User.create_user(username="testuser", email="invalid-email", password="TestPassword123")
                assert False, "应该抛出验证异常"
            except ValidationError:
                pass
            
            # 测试密码验证
            try:
                User.create_user(username="testuser", email="test@example.com", password="123")
                assert False, "应该抛出验证异常"
            except ValidationError:
                pass
            
            # 测试字典转换
            user = self.create_test_user(
                username="testuser5",
                email="test5@example.com",
                password="TestPassword123"
            )
            
            user_dict = user.to_dict()
            assert 'password_hash' not in user_dict
            assert user_dict['username'] == "testuser5"
            assert 'status' in user_dict
            
            public_dict = user.to_public_dict()
            assert 'password_hash' not in public_dict
            assert 'verification_token' not in public_dict
            
            print("✅ 数据验证测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 数据验证测试失败: {e}")
            return False


def main():
    """主测试函数"""
    print("🚀 开始用户模型测试...")
    
    # 创建测试实例
    test_instance = UserModelTest()
    success = test_instance.test_user_model()
    
    if success:
        print("\n🎉 用户模型测试全部通过！")
        return True
    else:
        print("\n❌ 用户模型测试失败，请检查代码。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
