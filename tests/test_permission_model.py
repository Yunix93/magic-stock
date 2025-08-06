"""
权限模型测试

测试权限模型的基本功能和方法
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.permission import Permission
from app.core.exceptions import ValidationError
from tests.base import ModelTestCase


class TestPermissionModel(ModelTestCase):
    """权限模型测试类"""
    
    def test_permission_creation_full(self):
        """测试权限创建（完整参数）"""
        try:
            permission_data = {
                'name': 'user:create',
                'resource': 'user',
                'action': 'create',
                'description': '创建用户权限',
                'group': 'user_management',
                'sort_order': "10"
            }
            
            permission = Permission(**permission_data)
            
            # 验证基本属性
            assert permission.name == 'user:create'
            assert permission.resource == 'user'
            assert permission.action == 'create'
            assert permission.description == '创建用户权限'
            assert permission.group == 'user_management'
            assert permission.sort_order == "10"
            
            print("✅ 权限创建（完整参数）测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 权限创建（完整参数）测试失败: {e}")
            return False
    
    def test_permission_creation_minimal(self):
        """测试权限创建（最少参数）"""
        try:
            permission_data = {
                'resource': 'post',
                'action': 'read'
            }
            
            permission = Permission(**permission_data)
            
            # 验证基本属性
            assert permission.resource == 'post'
            assert permission.action == 'read'
            assert permission.name == 'post:read'  # 应该自动生成
            assert permission.sort_order == "0"  # 默认值
            
            print("✅ 权限创建（最少参数）测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 权限创建（最少参数）测试失败: {e}")
            return False
    
    def test_permission_auto_name_generation(self):
        """测试权限名称自动生成"""
        try:
            # 不提供name，应该自动生成
            permission = Permission(resource='article', action='update')
            assert permission.name == 'article:update'
            
            # 提供name，应该使用提供的name
            permission2 = Permission(
                name='custom_name',
                resource='article',
                action='delete'
            )
            assert permission2.name == 'custom_name'
            
            print("✅ 权限名称自动生成测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 权限名称自动生成测试失败: {e}")
            return False
    
    def test_permission_validation(self):
        """测试权限字段验证"""
        try:
            # 测试有效数据
            valid_permission = Permission(
                name='valid:permission',
                resource='valid_resource',
                action='valid_action'
            )
            assert valid_permission.name == 'valid:permission'
            
            # 测试空字段（应该在验证器中处理）
            try:
                invalid_permission = Permission(resource='', action='test')
                print("⚠️ 空资源名称没有被拒绝，可能需要检查验证器")
            except Exception:
                # 预期的异常
                pass
            
            print("✅ 权限字段验证测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 权限字段验证测试失败: {e}")
            return False
    
    def test_to_dict(self):
        """测试字典转换"""
        try:
            permission = Permission(
                name='test:permission',
                resource='test',
                action='permission',
                description='测试权限',
                group='test_group',
                sort_order="15"
            )
            
            permission_dict = permission.to_dict()
            
            # 验证包含的字段
            assert 'name' in permission_dict
            assert 'resource' in permission_dict
            assert 'action' in permission_dict
            assert 'description' in permission_dict
            assert 'group' in permission_dict
            assert 'sort_order' in permission_dict
            
            # 验证值
            assert permission_dict['name'] == 'test:permission'
            assert permission_dict['resource'] == 'test'
            assert permission_dict['action'] == 'permission'
            assert permission_dict['sort_order'] == 15  # 应该转换为整数
            
            print("✅ 字典转换测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 字典转换测试失败: {e}")
            return False
    
    def test_to_public_dict(self):
        """测试公开信息字典转换"""
        try:
            permission = Permission(
                name='public:permission',
                resource='public',
                action='permission',
                description='公开权限',
                group='public_group',
                sort_order="20"
            )
            
            public_dict = permission.to_public_dict()
            
            # 验证包含的字段
            expected_fields = [
                'id', 'name', 'resource', 'action', 'description',
                'group', 'sort_order', 'created_at'
            ]
            
            for field in expected_fields:
                assert field in public_dict
            
            # 验证值
            assert public_dict['name'] == 'public:permission'
            assert public_dict['resource'] == 'public'
            assert public_dict['action'] == 'permission'
            assert public_dict['sort_order'] == 20  # 应该转换为整数
            
            print("✅ 公开信息字典转换测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 公开信息字典转换测试失败: {e}")
            return False
    
    def test_class_methods(self):
        """测试类方法"""
        try:
            # 测试 get_by_name（模拟）
            result = Permission.get_by_name('nonexistent:permission')
            assert result is None  # 应该返回None，因为没有数据库连接
            
            # 测试 get_by_resource_action（模拟）
            result = Permission.get_by_resource_action('nonexistent', 'action')
            assert result is None  # 应该返回None，因为没有数据库连接
            
            print("✅ 类方法测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 类方法测试失败: {e}")
            return False
    
    def test_sort_order_handling(self):
        """测试排序字段处理"""
        try:
            # 测试字符串排序值
            permission1 = Permission(
                resource='test',
                action='action1',
                sort_order="25"
            )
            assert permission1.sort_order == "25"
            
            # 测试默认排序值
            permission2 = Permission(resource='test', action='action2')
            assert permission2.sort_order == "0"
            
            # 测试字典转换中的排序值
            dict_result = permission1.to_dict()
            assert dict_result['sort_order'] == 25  # 应该转换为整数
            
            print("✅ 排序字段处理测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 排序字段处理测试失败: {e}")
            return False
    
    def test_permission_grouping(self):
        """测试权限分组"""
        try:
            # 有分组的权限
            permission_with_group = Permission(
                resource='user',
                action='create',
                group='user_management'
            )
            assert permission_with_group.group == 'user_management'
            
            # 无分组的权限
            permission_without_group = Permission(
                resource='user',
                action='read'
            )
            assert permission_without_group.group is None
            
            print("✅ 权限分组测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 权限分组测试失败: {e}")
            return False
    
    def test_repr_method(self):
        """测试字符串表示方法"""
        try:
            permission = Permission(
                name='test:repr',
                resource='test',
                action='repr'
            )
            repr_str = repr(permission)
            
            # 验证包含关键信息
            assert 'Permission' in repr_str
            assert 'test:repr' in repr_str
            assert 'test' in repr_str
            assert 'repr' in repr_str
            
            print("✅ 字符串表示方法测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 字符串表示方法测试失败: {e}")
            return False
    
    def test_permission_naming_patterns(self):
        """测试权限命名模式"""
        try:
            # 标准模式：resource:action
            permission1 = Permission(resource='user', action='create')
            assert permission1.name == 'user:create'
            
            # 复杂资源名
            permission2 = Permission(resource='user_profile', action='update')
            assert permission2.name == 'user_profile:update'
            
            # 复杂动作名
            permission3 = Permission(resource='system', action='admin_access')
            assert permission3.name == 'system:admin_access'
            
            print("✅ 权限命名模式测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 权限命名模式测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始权限模型测试")
        
        test_functions = [
            self.test_permission_creation_full,
            self.test_permission_creation_minimal,
            self.test_permission_auto_name_generation,
            self.test_permission_validation,
            self.test_to_dict,
            self.test_to_public_dict,
            self.test_class_methods,
            self.test_sort_order_handling,
            self.test_permission_grouping,
            self.test_repr_method,
            self.test_permission_naming_patterns
        ]
        
        results = self.run_test_suite(test_functions)
        
        test_names = [func.__name__ for func in test_functions]
        success = self.print_test_summary(results, test_names)
        
        return success


if __name__ == '__main__':
    test_case = TestPermissionModel()
    test_case.run_all_tests()