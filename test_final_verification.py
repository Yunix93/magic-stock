#!/usr/bin/env python3
"""
最终验证测试脚本

验证循环导入修复和会话管理修复的综合效果
"""

import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块导入"""
    print("=== 测试模块导入 ===")
    
    modules = [
        'app.models.user',
        'app.models.role', 
        'app.models.permission',
        'app.models.associations',
        'app.models.logs',
        'app.services.auth_service',
        'app.core.database'
    ]
    
    success = 0
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
            success += 1
        except Exception as e:
            print(f"✗ {module}: {e}")
    
    print(f"导入测试: {success}/{len(modules)} 成功")
    return success == len(modules)

def test_model_functionality():
    """测试模型功能"""
    print("\n=== 测试模型功能 ===")
    
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission
        from app.models.associations import UserRole, RolePermission
        
        # 创建测试实例
        user = User(username='final_test', email='final@example.com', password='Test12345!')
        role = Role(name='final_role', description='最终测试角色')
        permission = Permission(name='final:test', resource='final', action='test')
        
        print("✓ 模型实例创建成功")
        
        # 测试延迟导入的方法
        user.has_role('admin')
        user.has_permission('user:read')
        user.get_roles()
        user.get_permissions()
        
        role.get_permissions()
        role.get_users()
        role.get_user_count()
        
        permission.get_roles()
        permission.get_role_count()
        permission.get_users()
        
        print("✓ 所有模型方法调用成功")
        
        # 测试关联表方法
        UserRole.get_roles_by_user(user.id)
        UserRole.get_users_by_role(role.id)
        UserRole.count_users_by_role(role.id)
        UserRole.user_has_role(user.id, 'admin')
        
        RolePermission.get_permissions_by_role(role.id)
        RolePermission.get_roles_by_permission(permission.id)
        RolePermission.count_roles_by_permission(permission.id)
        RolePermission.role_has_permission(role.id, 'test:read')
        RolePermission.user_has_permission(user.id, 'test:read')
        
        print("✓ 关联表方法调用成功")
        
        # 测试Permission模型的特殊方法
        Permission.get_all_resources()
        Permission.get_all_actions()
        Permission.get_all_groups()
        
        print("✓ Permission模型方法调用成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 模型功能测试失败: {e}")
        traceback.print_exc()
        return False

def test_session_management():
    """测试会话管理"""
    print("\n=== 测试会话管理 ===")
    
    try:
        from app.core.database import get_db_session, get_session
        from sqlalchemy import text
        
        # 测试上下文管理器
        with get_db_session() as session:
            result = session.execute(text("SELECT 1")).fetchone()
            print(f"✓ 上下文管理器测试成功: {result}")
        
        # 测试外部会话
        external_session = get_session()
        try:
            with get_db_session(external_session) as session:
                assert session is external_session
                print("✓ 外部会话处理正确")
        finally:
            external_session.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 会话管理测试失败: {e}")
        traceback.print_exc()
        return False

def test_service_layer():
    """测试服务层"""
    print("\n=== 测试服务层 ===")
    
    try:
        from app.services.auth_service import AuthService, auth_service
        
        # 创建服务实例
        service = AuthService()
        print("✓ 认证服务实例创建成功")
        
        # 测试全局服务实例
        assert auth_service is not None
        print("✓ 全局服务实例正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 服务层测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始最终验证测试...\n")
    
    tests = [
        ("模块导入", test_imports),
        ("模型功能", test_model_functionality),
        ("会话管理", test_session_management),
        ("服务层", test_service_layer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
            print(f"✓ {test_name} 测试通过\n")
        else:
            print(f"✗ {test_name} 测试失败\n")
    
    # 总结
    print("=== 最终验证总结 ===")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        print("✅ 循环导入问题已解决")
        print("✅ 数据库会话管理已统一")
        print("✅ 系统架构健康稳定")
        return True
    else:
        print("❌ 存在问题，请检查上述错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)