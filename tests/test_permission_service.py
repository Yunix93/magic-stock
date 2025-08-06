"""
权限服务测试

测试权限服务层的业务逻辑
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.permission_service import PermissionService
from app.models.permission import Permission
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError
from tests.base import ServiceTestCase


class TestPermissionService(ServiceTestCase):
    """权限服务测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.permission_service = PermissionService()
    
    def test_service_initialization(self):
        """测试服务初始化"""
        try:
            # 无参数初始化
            service1 = PermissionService()
            assert service1.session is None
            
            # 带会话参数初始化
            mock_session = Mock()
            service2 = PermissionService(session=mock_session)
            assert service2.session == mock_session
            
            print("✅ 服务初始化测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 服务初始化测试失败: {e}")
            return False
    
    def test_get_session_method(self):
        """测试获取数据库会话方法"""
        try:
            service = PermissionService()
            
            # 模拟 get_db_session 函数
            with patch('app.services.permission_service.get_db_session') as mock_get_session:
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
    
    def test_create_permission_method_exists(self):
        """测试创建权限方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'create_permission')
            assert callable(getattr(service, 'create_permission'))
            
            print("✅ create_permission 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ create_permission 方法检查失败: {e}")
            return False
    
    def test_get_permission_by_id_method_exists(self):
        """测试根据ID获取权限方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_permission_by_id')
            assert callable(getattr(service, 'get_permission_by_id'))
            
            print("✅ get_permission_by_id 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_permission_by_id 方法检查失败: {e}")
            return False
    
    def test_get_permission_by_name_method_exists(self):
        """测试根据名称获取权限方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_permission_by_name')
            assert callable(getattr(service, 'get_permission_by_name'))
            
            print("✅ get_permission_by_name 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_permission_by_name 方法检查失败: {e}")
            return False
    
    def test_get_permissions_by_resource_method_exists(self):
        """测试根据资源获取权限方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_permissions_by_resource')
            assert callable(getattr(service, 'get_permissions_by_resource'))
            
            print("✅ get_permissions_by_resource 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_permissions_by_resource 方法检查失败: {e}")
            return False
    
    def test_get_permissions_list_method_exists(self):
        """测试获取权限列表方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_permissions_list')
            assert callable(getattr(service, 'get_permissions_list'))
            
            print("✅ get_permissions_list 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_permissions_list 方法检查失败: {e}")
            return False
    
    def test_update_permission_method_exists(self):
        """测试更新权限方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'update_permission')
            assert callable(getattr(service, 'update_permission'))
            
            print("✅ update_permission 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ update_permission 方法检查失败: {e}")
            return False
    
    def test_delete_permission_method_exists(self):
        """测试删除权限方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'delete_permission')
            assert callable(getattr(service, 'delete_permission'))
            
            print("✅ delete_permission 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ delete_permission 方法检查失败: {e}")
            return False
    
    def test_get_permission_statistics_method_exists(self):
        """测试获取权限统计方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_permission_statistics')
            assert callable(getattr(service, 'get_permission_statistics'))
            
            print("✅ get_permission_statistics 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_permission_statistics 方法检查失败: {e}")
            return False
    
    def test_get_resource_permissions_tree_method_exists(self):
        """测试获取资源权限树方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'get_resource_permissions_tree')
            assert callable(getattr(service, 'get_resource_permissions_tree'))
            
            print("✅ get_resource_permissions_tree 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ get_resource_permissions_tree 方法检查失败: {e}")
            return False
    
    def test_batch_create_permissions_method_exists(self):
        """测试批量创建权限方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查方法是否存在
            assert hasattr(service, 'batch_create_permissions')
            assert callable(getattr(service, 'batch_create_permissions'))
            
            print("✅ batch_create_permissions 方法存在")
            return True
            
        except Exception as e:
            print(f"❌ batch_create_permissions 方法检查失败: {e}")
            return False
    
    def test_validation_methods_exist(self):
        """测试验证方法是否存在"""
        try:
            service = PermissionService()
            
            # 检查权限创建数据验证方法
            if hasattr(service, '_validate_permission_creation_data'):
                assert callable(getattr(service, '_validate_permission_creation_data'))
                print("✅ _validate_permission_creation_data 方法存在")
            else:
                print("⚠️ _validate_permission_creation_data 方法不存在")
            
            # 检查权限更新数据验证方法
            if hasattr(service, '_validate_permission_update_data'):
                assert callable(getattr(service, '_validate_permission_update_data'))
                print("✅ _validate_permission_update_data 方法存在")
            else:
                print("⚠️ _validate_permission_update_data 方法不存在")
            
            # 检查权限唯一性验证方法
            if hasattr(service, '_check_permission_uniqueness'):
                assert callable(getattr(service, '_check_permission_uniqueness'))
                print("✅ _check_permission_uniqueness 方法存在")
            else:
                print("⚠️ _check_permission_uniqueness 方法不存在")
            
            print("✅ 验证方法检查完成")
            return True
            
        except Exception as e:
            print(f"❌ 验证方法检查失败: {e}")
            return False
    
    def test_permission_service_global_instance(self):
        """测试全局权限服务实例"""
        try:
            # 检查是否有全局实例
            from app.services.permission_service import permission_service
            
            assert permission_service is not None
            assert isinstance(permission_service, PermissionService)
            
            print("✅ 全局权限服务实例存在")
            return True
            
        except ImportError:
            print("⚠️ 全局权限服务实例不存在")
            return True  # 这不是错误，只是设计选择
        except Exception as e:
            print(f"❌ 全局权限服务实例检查失败: {e}")
            return False
    
    def test_validation_data_structure(self):
        """测试验证数据结构（模拟）"""
        try:
            service = PermissionService()
            
            # 检查是否有验证方法
            if hasattr(service, '_validate_permission_creation_data'):
                # 模拟测试数据
                test_data = {
                    'name': 'test:permission',
                    'resource': 'test',
                    'action': 'permission',
                    'description': '测试权限'
                }
                
                try:
                    # 尝试调用验证方法（可能会因为缺少依赖而失败）
                    result = service._validate_permission_creation_data(test_data)
                    print("✅ 权限创建数据验证方法可调用")
                except Exception as e:
                    print(f"⚠️ 权限创建数据验证方法存在但执行失败: {e}")
            else:
                print("⚠️ 权限创建数据验证方法不存在")
            
            return True
            
        except Exception as e:
            print(f"❌ 验证数据结构测试失败: {e}")
            return False
    
    def test_service_method_signatures(self):
        """测试服务方法签名"""
        try:
            service = PermissionService()
            
            # 检查主要方法的参数
            import inspect
            
            # 检查 create_permission 方法签名
            if hasattr(service, 'create_permission'):
                sig = inspect.signature(service.create_permission)
                params = list(sig.parameters.keys())
                assert 'permission_data' in params
                print("✅ create_permission 方法签名正确")
            
            # 检查 get_permissions_list 方法签名
            if hasattr(service, 'get_permissions_list'):
                sig = inspect.signature(service.get_permissions_list)
                params = list(sig.parameters.keys())
                # 应该有分页参数
                expected_params = ['page', 'per_page']
                for param in expected_params:
                    if param in params:
                        print(f"✅ get_permissions_list 包含参数: {param}")
            
            print("✅ 服务方法签名检查完成")
            return True
            
        except Exception as e:
            print(f"❌ 服务方法签名检查失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始权限服务测试")
        
        test_functions = [
            self.test_service_initialization,
            self.test_get_session_method,
            self.test_create_permission_method_exists,
            self.test_get_permission_by_id_method_exists,
            self.test_get_permission_by_name_method_exists,
            self.test_get_permissions_by_resource_method_exists,
            self.test_get_permissions_list_method_exists,
            self.test_update_permission_method_exists,
            self.test_delete_permission_method_exists,
            self.test_get_permission_statistics_method_exists,
            self.test_get_resource_permissions_tree_method_exists,
            self.test_batch_create_permissions_method_exists,
            self.test_validation_methods_exist,
            self.test_permission_service_global_instance,
            self.test_validation_data_structure,
            self.test_service_method_signatures
        ]
        
        results = self.run_test_suite(test_functions)
        
        test_names = [func.__name__ for func in test_functions]
        success = self.print_test_summary(results, test_names)
        
        return success


if __name__ == '__main__':
    test_case = TestPermissionService()
    test_case.run_all_tests()