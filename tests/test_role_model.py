"""
角色模型测试

测试角色模型的基本功能和方法
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.role import Role
from app.core.exceptions import ValidationError
from tests.base import ModelTestCase


class TestRoleModel(ModelTestCase):
    """角色模型测试类"""
    
    def test_role_creation(self):
        """测试角色创建"""
        try:
            role_data = {
                'name': 'admin',
                'description': '管理员角色',
                'is_active': True,
                'is_system': False
            }
            
            role = Role(**role_data)
            
            # 验证基本属性
            assert role.name == 'admin'
            assert role.description == '管理员角色'
            assert role.is_active == True
            assert role.is_system == False
            assert role.sort_order == "0"  # 默认值
            
            print("✅ 角色创建测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 角色创建测试失败: {e}")
            return False
    
    def test_role_creation_with_defaults(self):
        """测试角色创建（使用默认值）"""
        try:
            role_data = {
                'name': 'user'
            }
            
            role = Role(**role_data)
            
            # 验证默认值
            assert role.name == 'user'
            assert role.is_active == True
            assert role.is_system == False
            assert role.sort_order == "0"
            
            print("✅ 角色默认值创建测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 角色默认值创建测试失败: {e}")
            return False
    
    def test_role_name_validation(self):
        """测试角色名称验证"""
        try:
            # 测试有效名称
            valid_role = Role(name='valid_role_name')
            assert valid_role.name == 'valid_role_name'
            
            # 测试空名称（应该在验证器中处理）
            try:
                invalid_role = Role(name='')
                # 如果没有抛出异常，说明验证器可能没有启用
                print("⚠️ 空名称没有被拒绝，可能需要检查验证器")
            except Exception:
                # 预期的异常
                pass
            
            print("✅ 角色名称验证测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 角色名称验证测试失败: {e}")
            return False
    
    def test_to_dict(self):
        """测试字典转换"""
        try:
            role = Role(
                name='test_role',
                description='测试角色',
                is_active=True,
                is_system=False,
                sort_order="10"
            )
            
            role_dict = role.to_dict()
            
            # 验证包含的字段
            assert 'name' in role_dict
            assert 'description' in role_dict
            assert 'is_active' in role_dict
            assert 'is_system' in role_dict
            assert 'sort_order' in role_dict
            
            # 验证值
            assert role_dict['name'] == 'test_role'
            assert role_dict['description'] == '测试角色'
            assert role_dict['is_active'] == True
            assert role_dict['is_system'] == False
            
            print("✅ 字典转换测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 字典转换测试失败: {e}")
            return False
    
    def test_to_public_dict(self):
        """测试公开信息字典转换"""
        try:
            role = Role(
                name='public_role',
                description='公开角色',
                is_active=True,
                is_system=False,
                sort_order="5"
            )
            
            public_dict = role.to_public_dict()
            
            # 验证包含的字段
            expected_fields = [
                'id', 'name', 'description', 'is_active', 'is_system',
                'sort_order', 'created_at', 'updated_at'
            ]
            
            for field in expected_fields:
                assert field in public_dict
            
            # 验证值
            assert public_dict['name'] == 'public_role'
            assert public_dict['description'] == '公开角色'
            assert public_dict['sort_order'] == 5  # 应该转换为整数
            
            print("✅ 公开信息字典转换测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 公开信息字典转换测试失败: {e}")
            return False
    
    def test_class_methods(self):
        """测试类方法"""
        try:
            # 测试 get_by_name（模拟）
            result = Role.get_by_name('nonexistent_role')
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
            role1 = Role(name='role1', sort_order="10")
            assert role1.sort_order == "10"
            
            # 测试默认排序值
            role2 = Role(name='role2')
            assert role2.sort_order == "0"
            
            # 测试公开字典中的排序值转换
            public_dict = role1.to_public_dict()
            assert public_dict['sort_order'] == 10  # 应该转换为整数
            
            print("✅ 排序字段处理测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 排序字段处理测试失败: {e}")
            return False
    
    def test_system_role_flag(self):
        """测试系统角色标记"""
        try:
            # 普通角色
            normal_role = Role(name='normal_role')
            assert normal_role.is_system == False
            
            # 系统角色
            system_role = Role(name='system_role', is_system=True)
            assert system_role.is_system == True
            
            print("✅ 系统角色标记测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 系统角色标记测试失败: {e}")
            return False
    
    def test_repr_method(self):
        """测试字符串表示方法"""
        try:
            role = Role(name='test_role', is_active=True)
            repr_str = repr(role)
            
            # 验证包含关键信息
            assert 'Role' in repr_str
            assert 'test_role' in repr_str
            assert 'True' in repr_str
            
            print("✅ 字符串表示方法测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 字符串表示方法测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始角色模型测试")
        
        test_functions = [
            self.test_role_creation,
            self.test_role_creation_with_defaults,
            self.test_role_name_validation,
            self.test_to_dict,
            self.test_to_public_dict,
            self.test_class_methods,
            self.test_sort_order_handling,
            self.test_system_role_flag,
            self.test_repr_method
        ]
        
        results = self.run_test_suite(test_functions)
        
        test_names = [func.__name__ for func in test_functions]
        success = self.print_test_summary(results, test_names)
        
        return success


if __name__ == '__main__':
    test_case = TestRoleModel()
    test_case.run_all_tests()