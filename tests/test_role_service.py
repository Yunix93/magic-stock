"""
角色服务测试

测试角色服务层的业务逻辑
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.role_service import RoleService
from app.models.role import Role
from app.models.permission import Permission
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError
from tests.base import ServiceTestCase


class TestRoleService(ServiceTestCase):
    """角色服务测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.role_service = RoleService()
    
    def test_service_initialization(self):
        """测试服务初始化"""
        try:
            # 无参数初始化
            service1 = RoleService()
            assert service1.session is None
            
            # 带会话参数初始化
            mock_session = Mock()
            service2 = RoleService(session=mock_session)
            assert service2.session == mock_session
            
            print("✅ 服务初始化测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 服务初始化测试失败: {e}")
            return False
    
    def test_get_session_method(self):
        """测试获取数据库会话方法"""
        try:
            service = RoleService()
            
            # 模拟 get_db_session 函数
            with patch('app.services.role_service.get_db_session') as mock_get_session:
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
    
    def test_create_role_method_exists(self):
        """测试创建角色方法是否存在"""
        try:
            service = RoleService()
            
            # 检查方法是否存在
            assert hasattr(service, 'create_role')
            assert callable(getattr(service, 'create_role'))
            
            print("✅ create_role 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ create_role 方法检查失败: {e}")
            return False
    
    def test_get_role_by_id_method_exists(self):
        """测试根据ID获取角色方法是否存在"""
        try:
            service = RoleService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_role_by_id')
            assert callable(getattr(service, 'get_role_by_id'))
            
            print("✅ get_role_by_id 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_role_by_id 方法检查失败: {e}")
            return False
    
    def test_get_role_by_name_method_exists(self):
        """测试根据名称获取角色方法是否存在"""
        try:
            service = RoleService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_role_by_name')
            assert callable(getattr(service, 'get_role_by_name'))
            
            print("✅ get_role_by_name 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_role_by_name 方法检查失败: {e}")
            return False
    
    def test_get_roles_list_method_exists(self):
        """测试获取角色列表方法是否存在"""
        try:
            service = RoleService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_roles_list')
            assert callable(getattr(service, 'get_roles_list'))
            
            print("✅ get_roles_list 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_roles_list 方法检查失败: {e}")
            return False
    
    def test_update_role_method_exists(self):
        """测试更新角色方法是否存在"""
        try:
            service = RoleService()
            
            # 检查方法是否存在
            assert hasattr(service, 'update_role')
            assert callable(getattr(service, 'update_role'))
            
            print("✅ update_role 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ update_role 方法检查失败: {e}")
            return False
    
    def test_delete_role_method_exists(self):
        """测试删除角色方法是否存在"""
        try:
            service = RoleService()
            
            # 检查方法是否存在
            assert hasattr(service, 'delete_role')
            assert callable(getattr(service, 'delete_role'))
            
            print("✅ delete_role 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ delete_role 方法检查失败: {e}")
            return False
    
    def test_create_permission_method_exists(self):
        """测试创建权限方法是否存在"""
        try:
            service = RoleService()
            
            # 检查方法是否存在
            assert hasattr(service, 'create_permission')
            assert callable(getattr(service, 'create_permission'))
            
            print("✅ create_permission 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ create_permission 方法检查失败: {e}")
            return False
    
    def test_get_permission_methods_exist(self):
        """测试获取权限方法是否存在"""
        try:
            service = RoleService()
            
            # 检查根据ID获取权限方法
            assert hasattr(service, 'get_permission_by_id')
            assert callable(getattr(service, 'get_permission_by_id'))
            
            # 检查根据名称获取权限方法
            assert hasattr(service, 'get_permission_by_name')
            assert callable(getattr(service, 'get_permission_by_name'))
            
            # 检查获取权限列表方法
            assert hasattr(service, 'get_permissions_list')
            assert callable(getattr(service, 'get_permissions_list'))
            
            print("✅ 获取权限方法存在")
            return True
            
        except Exception as e:
            print(f"❌ 获取权限方法检查失败: {e}")
            return False
    
    def test_role_permission_assignment_methods_exist(self):
        """测试角色权限分配方法是否存在"""
        try:
            service = RoleService()
            
            # 检查分配权限方法
            assert hasattr(service, 'assign_permission_to_role')
            assert callable(getattr(service, 'assign_permission_to_role'))
            
            # 检查回收权限方法
            assert hasattr(service, 'revoke_permission_from_role')
            assert callable(getattr(service, 'revoke_permission_from_role'))
            
            print("✅ 角色权限分配方法存在")
            return True
            
        except Exception as e:
            print(f"❌ 角色权限分配方法检查失败: {e}")
            return False
    
    def test_get_role_permissions_method_exists(self):
        """测试获取角色权限方法是否存在"""
        try:
            service = RoleService()
            
            # 检查获取角色权限方法
            assert hasattr(service, 'get_role_permissions')
            assert callable(getattr(service, 'get_role_permissions'))
            
            print("✅ get_role_permissions 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_role_permissions 方法检查失败: {e}")
            return False
    
    def test_get_permission_roles_method_exists(self):
        """测试获取权限角色方法是否存在"""
        try:
            service = RoleService()
            
            # 检查获取权限角色方法
            assert hasattr(service, 'get_permission_roles')
            assert callable(getattr(service, 'get_permission_roles'))
            
            print("✅ get_permission_roles 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_permission_roles 方法检查失败: {e}")
            return False
    
    def test_batch_permission_methods_exist(self):
        """测试批量权限操作方法是否存在"""
        try:
            service = RoleService()
            
            # 检查批量分配权限方法
            assert hasattr(service, 'batch_assign_permissions_to_role')
            assert callable(getattr(service, 'batch_assign_permissions_to_role'))
            
            # 检查批量回收权限方法
            assert hasattr(service, 'batch_revoke_permissions_from_role')
            assert callable(getattr(service, 'batch_revoke_permissions_from_role'))
            
            print("✅ 批量权限操作方法存在")
            return True
            
        except Exception as e:
            print(f"❌ 批量权限操作方法检查失败: {e}")
            return False
    
    def test_validation_methods_exist(self):
        """测试验证方法是否存在（如果存在）"""
        try:
            service = RoleService()
            
            # 检查角色数据验证方法
            if hasattr(service, '_validate_role_creation_data'):
                assert callable(getattr(service, '_validate_role_creation_data'))
                print("✅ _validate_role_creation_data 方法存在")
            else:
                print("⚠️ _validate_role_creation_data 方法不存在")
            
            # 检查权限数据验证方法
            if hasattr(service, '_validate_permission_creation_data'):
                assert callable(getattr(service, '_validate_permission_creation_data'))
                print("✅ _validate_permission_creation_data 方法存在")
            else:
                print("⚠️ _validate_permission_creation_data 方法不存在")
            
            # 检查角色名称唯一性验证方法
            if hasattr(service, '_check_role_name_uniqueness'):
                assert callable(getattr(service, '_check_role_name_uniqueness'))
                print("✅ _check_role_name_uniqueness 方法存在")
            else:
                print("⚠️ _check_role_name_uniqueness 方法不存在")
            
            print("✅ 验证方法检查完成")
            return True
            
        except Exception as e:
            print(f"❌ 验证方法检查失败: {e}")
            return False
    
    def test_helper_methods_exist(self):
        """测试辅助方法是否存在（如果存在）"""
        try:
            service = RoleService()
            
            # 检查角色权限关联检查方法
            if hasattr(service, '_role_has_permission'):
                assert callable(getattr(service, '_role_has_permission'))
                print("✅ _role_has_permission 方法存在")
            else:
                print("⚠️ _role_has_permission 方法不存在")
            
            # 检查创建角色权限关联方法
            if hasattr(service, '_create_role_permission_association'):
                assert callable(getattr(service, '_create_role_permission_association'))
                print("✅ _create_role_permission_association 方法存在")
            else:
                print("⚠️ _create_role_permission_association 方法不存在")
            
            # 检查删除角色权限关联方法
            if hasattr(service, '_delete_role_permission_association'):
                assert callable(getattr(service, '_delete_role_permission_association'))
                print("✅ _delete_role_permission_association 方法存在")
            else:
                print("⚠️ _delete_role_permission_association 方法不存在")
            
            print("✅ 辅助方法检查完成")
            return True
            
        except Exception as e:
            print(f"❌ 辅助方法检查失败: {e}")
            return False
    
    def test_role_permission_table_method(self):
        """测试角色权限关联表方法（如果存在）"""
        try:
            service = RoleService()
            
            # 检查获取角色权限关联表方法
            if hasattr(service, '_get_role_permission_table'):
                assert callable(getattr(service, '_get_role_permission_table'))
                print("✅ _get_role_permission_table 方法存在")
            else:
                print("⚠️ _get_role_permission_table 方法不存在")
            
            return True
            
        except Exception as e:
            print(f"❌ 角色权限关联表方法检查失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始角色服务测试")
        
        test_functions = [
            self.test_service_initialization,
            self.test_get_session_method,
            self.test_create_role_method_exists,
            self.test_get_role_by_id_method_exists,
            self.test_get_role_by_name_method_exists,
            self.test_get_roles_list_method_exists,
            self.test_update_role_method_exists,
            self.test_delete_role_method_exists,
            self.test_create_permission_method_exists,
            self.test_get_permission_methods_exist,
            self.test_role_permission_assignment_methods_exist,
            self.test_get_role_permissions_method_exists,
            self.test_get_permission_roles_method_exists,
            self.test_batch_permission_methods_exist,
            self.test_validation_methods_exist,
            self.test_helper_methods_exist,
            self.test_role_permission_table_method
        ]
        
        results = self.run_test_suite(test_functions)
        
        test_names = [func.__name__ for func in test_functions]
        success = self.print_test_summary(results, test_names)
        
        return success


if __name__ == '__main__':
    test_case = TestRoleService()
    test_case.run_all_tests()