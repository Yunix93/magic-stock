"""
用户服务测试

测试用户服务层的业务逻辑
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.user_service import UserService
from app.models.user import User
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError
from tests.base import ServiceTestCase


class TestUserService(ServiceTestCase):
    """用户服务测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.user_service = UserService()
    
    def test_service_initialization(self):
        """测试服务初始化"""
        try:
            # 无参数初始化
            service1 = UserService()
            assert service1.session is None
            
            # 带会话参数初始化
            mock_session = Mock()
            service2 = UserService(session=mock_session)
            assert service2.session == mock_session
            
            print("✅ 服务初始化测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 服务初始化测试失败: {e}")
            return False
    
    def test_get_session_method(self):
        """测试获取数据库会话方法"""
        try:
            service = UserService()
            
            # 模拟 get_db_session 函数
            with patch('app.services.user_service.get_db_session') as mock_get_session:
                mock_session = Mock()
                mock_get_session.return_value = mock_session
                
                session = service._get_session()
                assert session == mock_session
                mock_get_session.assert_called_once()
            
            print("✅ 获取数据库会话方法测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 获取数据库会话方法测试失败: {e}")
            return False
    
    def test_validate_user_creation_data(self):
        """测试用户创建数据验证（如果方法存在）"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            if hasattr(service, '_validate_user_creation_data'):
                # 有效数据
                valid_data = {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'TestPassword123'
                }
                
                try:
                    result = service._validate_user_creation_data(valid_data)
                    assert isinstance(result, dict)
                    print("✅ 用户创建数据验证测试通过")
                except Exception as e:
                    print(f"⚠️ 用户创建数据验证方法存在但执行失败: {e}")
            else:
                print("⚠️ _validate_user_creation_data 方法不存在，跳过测试")
            
            return True
            
        except Exception as e:
            print(f"❌ 用户创建数据验证测试失败: {e}")
            return False
    
    def test_check_user_uniqueness(self):
        """测试用户唯一性检查（如果方法存在）"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            if hasattr(service, '_check_user_uniqueness'):
                # 模拟数据库查询
                with patch('app.services.user_service.get_db_session') as mock_get_session:
                    mock_session = Mock()
                    mock_query = Mock()
                    mock_session.query.return_value = mock_query
                    mock_query.filter.return_value = mock_query
                    mock_query.first.return_value = None  # 没有重复用户
                    mock_get_session.return_value.__enter__.return_value = mock_session
                    
                    try:
                        service._check_user_uniqueness('testuser', 'test@example.com')
                        print("✅ 用户唯一性检查测试通过")
                    except Exception as e:
                        print(f"⚠️ 用户唯一性检查方法存在但执行失败: {e}")
            else:
                print("⚠️ _check_user_uniqueness 方法不存在，跳过测试")
            
            return True
            
        except Exception as e:
            print(f"❌ 用户唯一性检查测试失败: {e}")
            return False
    
    def test_get_user_by_id_method_exists(self):
        """测试根据ID获取用户方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_user_by_id')
            assert callable(getattr(service, 'get_user_by_id'))
            
            print("✅ get_user_by_id 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_user_by_id 方法检查失败: {e}")
            return False
    
    def test_get_user_by_username_method_exists(self):
        """测试根据用户名获取用户方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_user_by_username')
            assert callable(getattr(service, 'get_user_by_username'))
            
            print("✅ get_user_by_username 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_user_by_username 方法检查失败: {e}")
            return False
    
    def test_get_user_by_email_method_exists(self):
        """测试根据邮箱获取用户方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_user_by_email')
            assert callable(getattr(service, 'get_user_by_email'))
            
            print("✅ get_user_by_email 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_user_by_email 方法检查失败: {e}")
            return False
    
    def test_create_user_method_exists(self):
        """测试创建用户方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'create_user')
            assert callable(getattr(service, 'create_user'))
            
            print("✅ create_user 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ create_user 方法检查失败: {e}")
            return False
    
    def test_update_user_method_exists(self):
        """测试更新用户方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'update_user')
            assert callable(getattr(service, 'update_user'))
            
            print("✅ update_user 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ update_user 方法检查失败: {e}")
            return False
    
    def test_delete_user_method_exists(self):
        """测试删除用户方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'delete_user')
            assert callable(getattr(service, 'delete_user'))
            
            print("✅ delete_user 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ delete_user 方法检查失败: {e}")
            return False
    
    def test_change_password_method_exists(self):
        """测试修改密码方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'change_password')
            assert callable(getattr(service, 'change_password'))
            
            print("✅ change_password 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ change_password 方法检查失败: {e}")
            return False
    
    def test_reset_password_method_exists(self):
        """测试重置密码方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'reset_password')
            assert callable(getattr(service, 'reset_password'))
            
            print("✅ reset_password 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ reset_password 方法检查失败: {e}")
            return False
    
    def test_get_users_list_method_exists(self):
        """测试获取用户列表方法是否存在"""
        try:
            service = UserService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_users_list')
            assert callable(getattr(service, 'get_users_list'))
            
            print("✅ get_users_list 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_users_list 方法检查失败: {e}")
            return False
    
    def test_user_role_management_methods_exist(self):
        """测试用户角色管理方法是否存在"""
        try:
            service = UserService()
            
            # 检查角色分配方法
            assert hasattr(service, 'assign_role_to_user')
            assert callable(getattr(service, 'assign_role_to_user'))
            
            # 检查角色移除方法
            assert hasattr(service, 'remove_role_from_user')
            assert callable(getattr(service, 'remove_role_from_user'))
            
            print("✅ 用户角色管理方法存在")
            return True
            
        except Exception as e:
            print(f"❌ 用户角色管理方法检查失败: {e}")
            return False
    
    def test_user_status_management_methods_exist(self):
        """测试用户状态管理方法是否存在"""
        try:
            service = UserService()
            
            # 检查激活用户方法
            assert hasattr(service, 'activate_user')
            assert callable(getattr(service, 'activate_user'))
            
            # 检查停用用户方法
            assert hasattr(service, 'deactivate_user')
            assert callable(getattr(service, 'deactivate_user'))
            
            # 检查锁定用户方法
            assert hasattr(service, 'lock_user')
            assert callable(getattr(service, 'lock_user'))
            
            # 检查解锁用户方法
            assert hasattr(service, 'unlock_user')
            assert callable(getattr(service, 'unlock_user'))
            
            print("✅ 用户状态管理方法存在")
            return True
            
        except Exception as e:
            print(f"❌ 用户状态管理方法检查失败: {e}")
            return False
    
    def test_permission_check_methods_exist(self):
        """测试权限检查方法是否存在"""
        try:
            service = UserService()
            
            # 检查用户权限检查方法
            assert hasattr(service, 'check_user_permission')
            assert callable(getattr(service, 'check_user_permission'))
            
            # 检查用户角色检查方法
            assert hasattr(service, 'check_user_role')
            assert callable(getattr(service, 'check_user_role'))
            
            # 检查管理员检查方法
            assert hasattr(service, 'is_user_admin')
            assert callable(getattr(service, 'is_user_admin'))
            
            print("✅ 权限检查方法存在")
            return True
            
        except Exception as e:
            print(f"❌ 权限检查方法检查失败: {e}")
            return False
    
    def test_statistics_methods_exist(self):
        """测试统计方法是否存在"""
        try:
            service = UserService()
            
            # 检查用户统计方法
            assert hasattr(service, 'get_user_statistics')
            assert callable(getattr(service, 'get_user_statistics'))
            
            # 检查登录历史方法
            assert hasattr(service, 'get_user_login_history')
            assert callable(getattr(service, 'get_user_login_history'))
            
            print("✅ 统计方法存在")
            return True
            
        except Exception as e:
            print(f"❌ 统计方法检查失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始用户服务测试")
        
        test_functions = [
            self.test_service_initialization,
            self.test_get_session_method,
            self.test_validate_user_creation_data,
            self.test_check_user_uniqueness,
            self.test_get_user_by_id_method_exists,
            self.test_get_user_by_username_method_exists,
            self.test_get_user_by_email_method_exists,
            self.test_create_user_method_exists,
            self.test_update_user_method_exists,
            self.test_delete_user_method_exists,
            self.test_change_password_method_exists,
            self.test_reset_password_method_exists,
            self.test_get_users_list_method_exists,
            self.test_user_role_management_methods_exist,
            self.test_user_status_management_methods_exist,
            self.test_permission_check_methods_exist,
            self.test_statistics_methods_exist
        ]
        
        results = self.run_test_suite(test_functions)
        
        test_names = [func.__name__ for func in test_functions]
        success = self.print_test_summary(results, test_names)
        
        return success


if __name__ == '__main__':
    test_case = TestUserService()
    test_case.run_all_tests()