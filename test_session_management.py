#!/usr/bin/env python3
"""
数据库会话管理测试脚本

测试修复后的统一会话管理机制
"""

import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_context_manager():
    """测试上下文管理器"""
    try:
        from app.core.database import get_db_session, get_session
        
        print("=== 测试上下文管理器 ===")
        
        # 测试无外部会话的情况
        with get_db_session() as session:
            print("✓ 上下文管理器创建新会话成功")
            # 模拟数据库操作
            from sqlalchemy import text
            result = session.execute(text("SELECT 1")).fetchone()
            print(f"✓ 数据库操作成功: {result}")
        
        # 测试有外部会话的情况
        external_session = get_session()
        try:
            with get_db_session(external_session) as session:
                print("✓ 上下文管理器使用外部会话成功")
                # 验证是同一个会话对象
                assert session is external_session, "会话对象不匹配"
                print("✓ 会话对象验证成功")
        finally:
            external_session.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 上下文管理器测试失败: {e}")
        traceback.print_exc()
        return False

def test_associations_methods():
    """测试关联表方法的会话管理"""
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission
        from app.models.associations import UserRole, RolePermission
        from app.core.database import get_session
        
        print("\n=== 测试关联表方法会话管理 ===")
        
        # 创建测试数据
        user = User(username='test_session', email='test_session@example.com', password='Test12345!')
        role = Role(name='test_session_role', description='测试会话角色')
        permission = Permission(name='test_session:read', resource='test_session', action='read')
        
        print("✓ 测试数据创建成功")
        
        # 测试无外部会话的方法调用
        roles = UserRole.get_roles_by_user(user.id)
        print(f"✓ UserRole.get_roles_by_user (无外部会话): {len(roles)} 个角色")
        
        users = UserRole.get_users_by_role(role.id)
        print(f"✓ UserRole.get_users_by_role (无外部会话): {len(users)} 个用户")
        
        count = UserRole.count_users_by_role(role.id)
        print(f"✓ UserRole.count_users_by_role (无外部会话): {count}")
        
        has_role = UserRole.user_has_role(user.id, 'admin')
        print(f"✓ UserRole.user_has_role (无外部会话): {has_role}")
        
        # 测试有外部会话的方法调用
        external_session = get_session()
        try:
            roles = UserRole.get_roles_by_user(user.id, session=external_session)
            print(f"✓ UserRole.get_roles_by_user (有外部会话): {len(roles)} 个角色")
            
            permissions = RolePermission.get_permissions_by_role(role.id, session=external_session)
            print(f"✓ RolePermission.get_permissions_by_role (有外部会话): {len(permissions)} 个权限")
            
            has_permission = RolePermission.role_has_permission(role.id, 'test:read', session=external_session)
            print(f"✓ RolePermission.role_has_permission (有外部会话): {has_permission}")
            
        finally:
            external_session.close()
        
        print("✓ 所有关联表方法会话管理测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 关联表方法测试失败: {e}")
        traceback.print_exc()
        return False

def test_permission_methods():
    """测试Permission模型方法的会话管理"""
    try:
        from app.models.permission import Permission
        
        print("\n=== 测试Permission模型会话管理 ===")
        
        # 测试修复后的方法
        resources = Permission.get_all_resources()
        print(f"✓ Permission.get_all_resources: {len(resources)} 个资源")
        
        actions = Permission.get_all_actions()
        print(f"✓ Permission.get_all_actions: {len(actions)} 个操作")
        
        groups = Permission.get_all_groups()
        print(f"✓ Permission.get_all_groups: {len(groups)} 个分组")
        
        print("✓ Permission模型会话管理测试通过")
        return True
        
    except Exception as e:
        print(f"✗ Permission模型测试失败: {e}")
        traceback.print_exc()
        return False

def test_model_integration():
    """测试模型集成的会话管理"""
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission
        from app.core.database import get_session
        
        print("\n=== 测试模型集成会话管理 ===")
        
        # 创建测试实例
        user = User(username='integration_test', email='integration@example.com', password='Test12345!')
        role = Role(name='integration_role', description='集成测试角色')
        permission = Permission(name='integration:test', resource='integration', action='test')
        
        # 测试用户模型的方法（这些方法内部调用关联表方法）
        user_roles = user.get_roles()
        print(f"✓ user.get_roles: {len(user_roles)} 个角色")
        
        user_permissions = user.get_permissions()
        print(f"✓ user.get_permissions: {len(user_permissions)} 个权限")
        
        has_role = user.has_role('admin')
        print(f"✓ user.has_role: {has_role}")
        
        has_permission = user.has_permission('user:read')
        print(f"✓ user.has_permission: {has_permission}")
        
        # 测试角色模型的方法
        role_permissions = role.get_permissions()
        print(f"✓ role.get_permissions: {len(role_permissions)} 个权限")
        
        role_users = role.get_users()
        print(f"✓ role.get_users: {len(role_users)} 个用户")
        
        # 测试权限模型的方法
        permission_roles = permission.get_roles()
        print(f"✓ permission.get_roles: {len(permission_roles)} 个角色")
        
        permission_users = permission.get_users()
        print(f"✓ permission.get_users: {len(permission_users)} 个用户")
        
        print("✓ 模型集成会话管理测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 模型集成测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始数据库会话管理测试...\n")
    
    tests = [
        ("上下文管理器", test_context_manager),
        ("关联表方法", test_associations_methods),
        ("Permission模型", test_permission_methods),
        ("模型集成", test_model_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"运行测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✓ {test_name} 测试通过\n")
        else:
            print(f"✗ {test_name} 测试失败\n")
    
    # 总结
    print("=== 测试总结 ===")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有会话管理测试通过，统一上下文管理器模式工作正常")
        return True
    else:
        print("✗ 存在会话管理问题，请检查上述错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)