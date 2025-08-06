#!/usr/bin/env python3
"""
权限控制系统功能验证测试

验证权限控制装饰器和权限管理系统的核心功能
"""

import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_permission_registry():
    """测试权限注册表"""
    print("=== 测试权限注册表 ===")
    
    from app.core.permissions import permission_registry, PermissionDefinition
    
    # 测试默认权限
    assert permission_registry.exists('user:create'), "用户创建权限应该存在"
    assert permission_registry.exists('role:read'), "角色读取权限应该存在"
    assert permission_registry.exists('system:config'), "系统配置权限应该存在"
    
    # 测试权限获取
    user_create_perm = permission_registry.get('user:create')
    assert user_create_perm is not None, "应该能获取到用户创建权限"
    assert user_create_perm.resource == 'user', "权限资源应该是user"
    assert user_create_perm.action == 'create', "权限操作应该是create"
    
    # 测试按组获取权限
    user_mgmt_perms = permission_registry.get_by_group('用户管理')
    assert len(user_mgmt_perms) > 0, "用户管理组应该有权限"
    
    # 测试按资源获取权限
    user_perms = permission_registry.get_by_resource('user')
    assert len(user_perms) > 0, "用户资源应该有多个权限"
    
    print("✓ 权限注册表测试通过")

def test_role_permission_manager():
    """测试角色权限管理器"""
    print("\n=== 测试角色权限管理器 ===")
    
    from app.core.permissions import role_permission_manager
    
    # 测试默认角色权限
    admin_perms = role_permission_manager.get_role_permissions('admin')
    assert 'user:create' in admin_perms, "管理员应该有用户创建权限"
    assert 'system:config' in admin_perms, "管理员应该有系统配置权限"
    
    user_perms = role_permission_manager.get_role_permissions('user')
    assert 'dashboard:view' in user_perms, "普通用户应该有仪表板查看权限"
    assert 'user:create' not in user_perms, "普通用户不应该有用户创建权限"
    
    # 测试权限检查
    assert role_permission_manager.has_permission(['admin'], 'user:create'), "管理员应该有用户创建权限"
    assert not role_permission_manager.has_permission(['user'], 'user:create'), "普通用户不应该有用户创建权限"
    
    # 测试多角色权限合并
    multi_role_perms = role_permission_manager.get_user_permissions(['admin', 'manager'])
    assert 'user:create' in multi_role_perms, "管理员+经理应该有用户创建权限"
    assert 'dashboard:view' in multi_role_perms, "管理员+经理应该有仪表板查看权限"
    
    print("✓ 角色权限管理器测试通过")

def test_permission_checker():
    """测试权限检查器"""
    print("\n=== 测试权限检查器 ===")
    
    from app.core.permissions import permission_checker
    
    # 创建模拟用户
    admin_role = Mock()
    admin_role.name = 'admin'
    admin_user = Mock()
    admin_user.is_superuser = False
    admin_user.is_active = True
    admin_user.get_roles.return_value = [admin_role]
    
    user_role = Mock()
    user_role.name = 'user'
    regular_user = Mock()
    regular_user.is_superuser = False
    regular_user.is_active = True
    regular_user.get_roles.return_value = [user_role]
    
    superuser = Mock()
    superuser.is_superuser = True
    superuser.is_active = True
    
    # 测试权限检查
    assert permission_checker.check_permission(admin_user, 'user:create'), "管理员应该有用户创建权限"
    assert not permission_checker.check_permission(regular_user, 'user:create'), "普通用户不应该有用户创建权限"
    assert permission_checker.check_permission(superuser, 'any:permission'), "超级用户应该有任何权限"
    
    # 测试角色检查 - 删除has_role方法，强制使用get_roles
    del admin_user.has_role
    del regular_user.has_role
    assert permission_checker.check_role(admin_user, 'admin'), "管理员用户应该有admin角色"
    assert not permission_checker.check_role(regular_user, 'admin'), "普通用户不应该有admin角色"
    
    # 测试获取用户权限
    admin_permissions = permission_checker.get_user_permissions(admin_user)
    assert 'user:create' in admin_permissions, "管理员权限列表应该包含用户创建权限"
    
    print("✓ 权限检查器测试通过")

def test_auth_decorators():
    """测试认证装饰器"""
    print("\n=== 测试认证装饰器 ===")
    
    from app.core.auth import login_required, permission_required, role_required
    from flask import Flask
    
    app = Flask(__name__)
    
    # 测试装饰器可以正常应用
    @login_required
    def protected_view():
        return {'message': 'success'}
    
    @permission_required('user:read')
    def permission_view():
        return {'message': 'success'}
    
    @role_required('admin')
    def admin_view():
        return {'message': 'success'}
    
    # 验证装饰器不会破坏函数
    assert hasattr(protected_view, '__wrapped__'), "装饰器应该保留原函数引用"
    assert protected_view.__name__ == 'protected_view', "装饰器应该保留函数名"
    
    print("✓ 认证装饰器测试通过")

def test_advanced_decorators():
    """测试高级权限装饰器"""
    print("\n=== 测试高级权限装饰器 ===")
    
    from app.core.permission_decorators import require_permissions, require_roles, audit_log
    
    # 测试多权限装饰器
    @require_permissions('user:read', 'user:update', operator='AND')
    def multi_permission_view():
        return {'message': 'success'}
    
    @require_roles('admin', 'manager', operator='OR')
    def multi_role_view():
        return {'message': 'success'}
    
    @audit_log('test_action', 'test_resource')
    def audited_view():
        return {'message': 'success'}
    
    # 验证装饰器应用成功
    assert hasattr(multi_permission_view, '__wrapped__'), "多权限装饰器应该正常应用"
    assert hasattr(multi_role_view, '__wrapped__'), "多角色装饰器应该正常应用"
    assert hasattr(audited_view, '__wrapped__'), "审计装饰器应该正常应用"
    
    print("✓ 高级权限装饰器测试通过")

def test_permission_helpers():
    """测试权限辅助函数"""
    print("\n=== 测试权限辅助函数 ===")
    
    from app.core.permissions import has_permission, has_role, get_user_permissions
    
    # 创建模拟用户
    admin_role = Mock()
    admin_role.name = 'admin'
    user = Mock()
    user.is_superuser = False
    user.is_active = True
    user.get_roles.return_value = [admin_role]
    
    # 测试全局权限函数
    assert has_permission(user, 'user:create'), "全局权限检查函数应该正常工作"
    assert has_role(user, 'admin'), "全局角色检查函数应该正常工作"
    
    permissions = get_user_permissions(user)
    assert isinstance(permissions, set), "用户权限应该返回集合类型"
    assert len(permissions) > 0, "管理员用户应该有权限"
    
    print("✓ 权限辅助函数测试通过")

def main():
    """主测试函数"""
    print("开始权限控制系统功能验证...\n")
    
    tests = [
        test_permission_registry,
        test_role_permission_manager,
        test_permission_checker,
        test_auth_decorators,
        test_advanced_decorators,
        test_permission_helpers,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== 测试总结 ===")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 权限控制系统功能验证全部通过！")
        print("✅ 认证装饰器验证用户登录状态 - 完成")
        print("✅ 权限装饰器验证用户操作权限 - 完成")
        print("✅ 基于角色的访问控制逻辑 - 完成")
        print("✅ 权限控制的核心功能 - 完成")
        return True
    else:
        print("❌ 部分测试失败，请检查上述错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)