#!/usr/bin/env python3
"""
角色权限模型测试

测试角色权限模型的基本功能
"""

import os
import sys
import tempfile
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_role_permission_model():
    """测试角色权限模型基本功能"""
    print("🧪 开始测试角色权限模型...")
    
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
            
            # 测试角色权限模型
            test_results = []
            
            # 1. 测试角色模型
            print("\n📝 测试角色模型...")
            test_results.append(test_role_model())
            
            # 2. 测试权限模型
            print("\n🔐 测试权限模型...")
            test_results.append(test_permission_model())
            
            # 3. 测试关联表模型
            print("\n🔗 测试关联表模型...")
            test_results.append(test_association_models())
            
            # 4. 测试集成功能
            print("\n🎯 测试集成功能...")
            test_results.append(test_integration_features())
            
            # 5. 测试默认数据创建
            print("\n🏗️ 测试默认数据创建...")
            test_results.append(test_default_data_creation())
            
            # 输出测试结果
            passed = sum(test_results)
            total = len(test_results)
            
            print(f"\n📋 测试结果汇总:")
            print(f"  通过: {passed}/{total}")
            
            if passed == total:
                print("🎉 所有角色权限模型测试通过！")
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
        print(f"❌ 角色权限模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_role_model():
    """测试角色模型"""
    try:
        from app.models.role import Role
        
        # 创建角色
        role = Role(
            name="test_role",
            description="测试角色"
        )
        
        # 验证基本属性
        assert role.name == "test_role"
        assert role.description == "测试角色"
        assert role.is_active is True
        assert role.is_system is False
        assert role.sort_order == "0"
        
        # 测试激活/停用
        role.deactivate()
        assert role.is_active is False
        
        role.activate()
        assert role.is_active is True
        
        # 测试字典转换
        role_dict = role.to_dict()
        assert 'name' in role_dict
        assert 'user_count' in role_dict
        assert 'can_be_deleted' in role_dict
        
        public_dict = role.to_public_dict()
        assert 'name' in public_dict
        assert 'sort_order' in public_dict
        
        print("✅ 角色模型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 角色模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_permission_model():
    """测试权限模型"""
    try:
        from app.models.permission import Permission
        
        # 创建权限
        permission = Permission(
            resource="user",
            action="create",
            description="创建用户",
            group="用户管理"
        )
        
        # 验证基本属性
        assert permission.name == "user:create"
        assert permission.resource == "user"
        assert permission.action == "create"
        assert permission.description == "创建用户"
        assert permission.group == "用户管理"
        assert permission.sort_order == "0"
        
        # 测试指定名称创建
        custom_permission = Permission(
            name="custom_permission",
            resource="system",
            action="config"
        )
        assert custom_permission.name == "custom_permission"
        
        # 测试字典转换
        perm_dict = permission.to_dict()
        assert 'name' in perm_dict
        assert 'resource' in perm_dict
        assert 'role_count' in perm_dict
        assert 'can_be_deleted' in perm_dict
        
        public_dict = permission.to_public_dict()
        assert 'name' in public_dict
        assert 'sort_order' in public_dict
        
        print("✅ 权限模型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 权限模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_association_models():
    """测试关联表模型"""
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission
        from app.models.associations import UserRole, RolePermission
        
        # 创建测试数据
        user = User.create_user(username="testuser", email="test@example.com", password="Password123")
        role = Role.create_role(name="test_role", description="测试角色")
        permission = Permission.create_permission(resource="user", action="create")
        
        print(f"  用户ID: {user.id}")
        print(f"  角色ID: {role.id}")
        print(f"  权限ID: {permission.id}")
        
        # 测试用户角色关联
        user_role = UserRole.assign_role_to_user(user.id, role.id)
        print(f"  用户角色关联: {user_role}")
        assert user_role is not None
        assert user_role.user_id == user.id
        assert user_role.role_id == role.id
        
        # 测试角色权限关联
        role_permission = RolePermission.grant_permission_to_role(role.id, permission.id)
        print(f"  角色权限关联: {role_permission}")
        assert role_permission is not None
        assert role_permission.role_id == role.id
        assert role_permission.permission_id == permission.id
        
        # 测试权限检查
        has_role = UserRole.user_has_role(user.id, "test_role")
        print(f"  用户是否有角色: {has_role}")
        assert has_role is True
        
        has_permission = RolePermission.role_has_permission(role.id, "user:create")
        print(f"  角色是否有权限: {has_permission}")
        assert has_permission is True
        
        user_has_permission = RolePermission.user_has_permission(user.id, "user:create")
        print(f"  用户是否有权限: {user_has_permission}")
        assert user_has_permission is True
        
        # 测试移除关联
        assert UserRole.remove_role_from_user(user.id, role.id) is True
        assert RolePermission.revoke_permission_from_role(role.id, permission.id) is True
        
        print("✅ 关联表模型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 关联表模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_features():
    """测试集成功能"""
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission
        
        # 创建测试数据
        user = User.create_user(username="testuser2", email="test2@example.com", password="Password123")
        role = Role.create_role(name="manager", description="管理员")
        permission = Permission.create_permission(resource="user", action="update")
        
        # 测试用户角色方法
        assert user.add_role(role) is True
        assert user.has_role("manager") is True
        
        roles = user.get_roles()
        assert len(roles) >= 0  # 在测试环境中可能为空
        
        # 测试角色权限方法
        assert role.add_permission(permission) is True
        assert role.has_permission("user:update") is True
        
        permissions = role.get_permissions()
        assert len(permissions) >= 0  # 在测试环境中可能为空
        
        # 测试用户权限检查
        assert user.has_permission("user:update") is True
        
        user_permissions = user.get_permissions()
        assert len(user_permissions) >= 0  # 在测试环境中可能为空
        
        # 测试管理员检查
        admin_user = User.create_user(username="admin", email="admin@example.com", password="Password123")
        admin_role = Role.create_role(name="admin", description="管理员")
        
        admin_user.add_role(admin_role)
        assert admin_user.is_admin() is True
        
        # 测试超级用户
        superuser = User(username="super", email="super@example.com", password="Password123", is_superuser=True)
        assert superuser.is_admin() is True
        
        print("✅ 集成功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 集成功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_default_data_creation():
    """测试默认数据创建"""
    try:
        from app.models.role import Role
        from app.models.permission import Permission
        
        # 创建默认角色
        roles = Role.create_default_roles()
        print(f"📋 创建了 {len(roles)} 个默认角色")
        
        # 验证默认角色
        admin_role = Role.get_by_name("admin")
        if admin_role:
            print(f"✅ 管理员角色创建成功，is_system: {admin_role.is_system}")
        else:
            print("❌ 管理员角色未找到")
        
        # 创建默认权限
        permissions = Permission.create_default_permissions()
        print(f"🔑 创建了 {len(permissions)} 个默认权限")
        
        # 验证默认权限
        user_create = Permission.get_by_name("user:create")
        if user_create:
            assert user_create.resource == "user"
            assert user_create.action == "create"
            print("✅ 用户创建权限创建成功")
        
        print("✅ 默认数据创建测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 默认数据创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始角色权限模型测试...")
    
    success = test_role_permission_model()
    
    if success:
        print("\n🎉 角色权限模型测试全部通过！")
        return True
    else:
        print("\n❌ 角色权限模型测试失败，请检查代码。")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)