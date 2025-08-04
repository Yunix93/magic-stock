"""
测试基类

提供统一的测试基础设施，消除测试代码重复
"""

import os
import sys
import tempfile
import pytest
from abc import ABC

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BaseTestCase(ABC):
    """测试基类，提供统一的测试基础设施"""
    
    @classmethod
    def setup_test_database(cls):
        """统一的数据库初始化逻辑"""
        # 使用统一的配置管理
        from app.core.config_manager import config_manager
        
        # 创建应用实例，使用临时数据库
        from app import create_app
        app, server = create_app('testing')
        
        # 使用临时数据库文件
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        
        return app, server, db_fd, db_path
    
    @classmethod
    def init_database_tables(cls, server):
        """初始化数据库表结构"""
        with server.app_context():
            # 初始化数据库
            from app.models.base import init_database, create_tables
            database_url = server.config.get('SQLALCHEMY_DATABASE_URI')
            engine, session = init_database(database_url)
            
            # 使用统一的模型导入
            from app.models import User, Role, Permission, LoginLog, OperationLog, UserRole, RolePermission
            
            create_tables()
            return engine, session
    
    @classmethod
    def cleanup_database(cls, db_fd, db_path):
        """清理临时数据库文件"""
        try:
            os.close(db_fd)
            os.unlink(db_path)
        except:
            pass
    
    @classmethod
    def create_test_user(cls, **kwargs):
        """创建测试用户的工厂方法"""
        from app.models.user import User
        
        default_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'full_name': 'Test User'
        }
        default_data.update(kwargs)
        
        return User.create_user(**default_data)
    
    @classmethod
    def create_test_role(cls, **kwargs):
        """创建测试角色的工厂方法"""
        from app.models.role import Role
        
        default_data = {
            'name': 'test_role',
            'description': 'Test Role'
        }
        default_data.update(kwargs)
        
        return Role.create_role(**default_data)
    
    @classmethod
    def create_test_permission(cls, **kwargs):
        """创建测试权限的工厂方法"""
        from app.models.permission import Permission
        
        default_data = {
            'name': 'test.permission',
            'resource': 'test',
            'action': 'permission',
            'description': 'Test Permission'
        }
        default_data.update(kwargs)
        
        return Permission.create_permission(**default_data)
    
    def run_test_suite(self, test_functions):
        """运行测试套件"""
        test_results = []
        
        for test_func in test_functions:
            try:
                print(f"\n🧪 运行测试: {test_func.__name__}")
                result = test_func()
                test_results.append(result)
                if result:
                    print(f"✅ {test_func.__name__} 通过")
                else:
                    print(f"❌ {test_func.__name__} 失败")
            except Exception as e:
                print(f"❌ {test_func.__name__} 异常: {e}")
                test_results.append(False)
        
        return test_results
    
    def print_test_summary(self, test_results, test_names=None):
        """打印测试结果汇总"""
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"\n📋 测试结果汇总:")
        print(f"  通过: {passed}/{total}")
        
        if test_names:
            for i, (name, result) in enumerate(zip(test_names, test_results)):
                status = "✅" if result else "❌"
                print(f"  {status} {name}")
        
        if passed == total:
            print("🎉 所有测试通过！")
            return True
        else:
            print("❌ 部分测试失败")
            return False


class ModelTestCase(BaseTestCase):
    """模型测试基类"""
    
    def test_model_creation(self, model_class, test_data):
        """通用模型创建测试"""
        try:
            instance = model_class(**test_data)
            assert instance is not None
            return True
        except Exception as e:
            print(f"模型创建测试失败: {e}")
            return False
    
    def test_model_validation(self, model_class, invalid_data_list):
        """通用模型验证测试"""
        try:
            for invalid_data in invalid_data_list:
                try:
                    model_class(**invalid_data)
                    return False  # 应该抛出异常
                except Exception:
                    pass  # 预期的异常
            return True
        except Exception as e:
            print(f"模型验证测试失败: {e}")
            return False


class ServiceTestCase(BaseTestCase):
    """服务测试基类"""
    
    def setup_service_test(self, service_class):
        """设置服务测试环境"""
        app, server, db_fd, db_path = self.setup_test_database()
        
        with server.app_context():
            engine, session = self.init_database_tables(server)
            service_instance = service_class()
            
            return app, server, db_fd, db_path, service_instance
    
    def test_service_method(self, service_instance, method_name, test_cases):
        """通用服务方法测试"""
        method = getattr(service_instance, method_name)
        results = []
        
        for test_case in test_cases:
            try:
                args = test_case.get('args', [])
                kwargs = test_case.get('kwargs', {})
                expected = test_case.get('expected')
                should_raise = test_case.get('should_raise', False)
                
                if should_raise:
                    try:
                        method(*args, **kwargs)
                        results.append(False)  # 应该抛出异常但没有
                    except Exception:
                        results.append(True)  # 预期的异常
                else:
                    result = method(*args, **kwargs)
                    if expected is not None:
                        results.append(result == expected)
                    else:
                        results.append(result is not None)
                        
            except Exception as e:
                print(f"服务方法测试失败: {e}")
                results.append(False)
        
        return all(results)


class IntegrationTestCase(BaseTestCase):
    """集成测试基类"""
    
    def setup_integration_test(self):
        """设置集成测试环境"""
        app, server, db_fd, db_path = self.setup_test_database()
        
        with server.app_context():
            engine, session = self.init_database_tables(server)
            
            # 创建测试数据
            self.setup_test_data()
            
            return app, server, db_fd, db_path
    
    def setup_test_data(self):
        """设置测试数据"""
        # 创建测试用户
        self.test_user = self.create_test_user()
        
        # 创建测试角色
        self.test_role = self.create_test_role()
        
        # 创建测试权限
        self.test_permission = self.create_test_permission()
        
        # 建立关联关系
        self.test_user.add_role(self.test_role)
        self.test_role.add_permission(self.test_permission)
    
    def test_workflow(self, workflow_steps):
        """测试工作流程"""
        results = []
        
        for step in workflow_steps:
            try:
                step_name = step.get('name', 'Unknown Step')
                step_func = step.get('function')
                step_args = step.get('args', [])
                step_kwargs = step.get('kwargs', {})
                
                print(f"  执行步骤: {step_name}")
                result = step_func(*step_args, **step_kwargs)
                results.append(result)
                
                if not result:
                    print(f"  ❌ 步骤失败: {step_name}")
                    break
                else:
                    print(f"  ✅ 步骤成功: {step_name}")
                    
            except Exception as e:
                print(f"  ❌ 步骤异常: {step_name} - {e}")
                results.append(False)
                break
        
        return all(results)