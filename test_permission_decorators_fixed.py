#!/usr/bin/env python3
"""
修复的权限装饰器测试

专门测试权限装饰器的核心逻辑
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_permission_registry():
    """测试权限注册表"""
    from app.core.permissions import PermissionRegistry, PermissionDefinition
    
    # 创建权限注册表
    registry = PermissionRegistry()
    
    # 检查默认权限
    assert registry.exists('user:create'), "默认权限user:create不存在"
    assert registry.exists('role:read'), "默认权限role:read不存在"
    assert registry.exists('system:config'), "默认权限system:config不存在"
    
    # 测试自定义权限注册
    custom_perm = PermissionDefinition(
        "test:action", "test", "action", "测试权限", "测试组"
    )
    registry.register(custom_perm)
    
    assert registry.exists('test:action'), "自定义权限注册失败"
    assert registry.get('test:action') == custom_perm, "权限获取失败"


def test_role_permission_manager():
    """测试角色权限管理器"""
    from app.core.permissions import PermissionRegistry, RolePermissionManager
    
    # 创建管理器
    registry = PermissionRegistry()
    manager = RolePermissionManager(registry)
    
    # 检查默认角色权限
    admin_perms = manager.get_role_permissions('admin')
    assert 'user:create' in admin_perms, "管理员应该有user:create权限"
    assert 'system:config' in admin_perms, "管理员应该有system:config权限"
    
    # 测试权限分配
    manager.assign_permission_to_role('test_role', 'user:read')
    assert manager.has_permission(['test_role'], 'user:read'), "权限分配失败"
    
    # 测试权限撤销
    manager.revoke_permission_from_role('test_role', 'user:read')
    assert not manager.has_permission(['test_role'], 'user:read'), "权限撤销失败"


def test_permission_checker():
    """测试权限检查器"""
    from app.core.permissions import (
        PermissionRegistry, RolePermissionManager, PermissionChecker
    )
    
    # 创建检查器
    registry = PermissionRegistry()
    manager = RolePermissionManager(registry)
    checker = PermissionChecker(registry, manager)
    
    # 创建模拟用户
    mock_user = Mock()
    mock_user.is_superuser = False
    mock_user.is_active = True
    
    # 模拟用户角色
    mock_role = Mock()
    mock_role.name = 'admin'
    mock_user.get_roles.return_value = [mock_role]
    
    # 测试权限检查
    has_permission = checker.check_permission(mock_user, 'user:create')
    assert has_permission, "管理员应该有user:create权限"
    
    # 测试超级用户
    superuser = Mock()
    superuser.is_superuser = True
    superuser.is_active = True
    
    has_any_permission = checker.check_permission(superuser, 'any:permission')
    assert has_any_permission, "超级用户应该有所有权限"
    
    # 测试非活跃用户
    inactive_user = Mock()
    inactive_user.is_superuser = False
    inactive_user.is_active = False
    
    has_no_permission = checker.check_permission(inactive_user, 'user:read')
    assert not has_no_permission, "非活跃用户不应该有任何权限"


def test_basic_auth_decorators():
    """测试基础认证装饰器"""
    from app.core.auth import login_required, permission_required
    
    # 测试装饰器导入
    assert callable(login_required), "login_required装饰器导入失败"
    assert callable(permission_required), "permission_required装饰器导入失败"
    
    # 测试装饰器应用
    @login_required
    def test_view():
        return {'success': True}
    
    assert callable(test_view), "装饰器应用失败"


def test_advanced_permission_decorators():
    """测试高级权限装饰器"""
    from app.core.permission_decorators import (
        require_permissions, require_roles, audit_log
    )
    
    # 测试装饰器导入
    assert callable(require_permissions), "require_permissions装饰器导入失败"
    assert callable(require_roles), "require_roles装饰器导入失败"
    assert callable(audit_log), "audit_log装饰器导入失败"
    
    # 测试装饰器应用
    @require_permissions('user:read', 'user:write')
    def test_multi_permission_view():
        return {'success': True}
    
    @require_roles('admin', 'manager')
    def test_multi_role_view():
        return {'success': True}
    
    @audit_log('test_action', 'test_resource')
    def test_audit_view():
        return {'success': True}
    
    assert callable(test_multi_permission_view), "多权限装饰器应用失败"
    assert callable(test_multi_role_view), "多角色装饰器应用失败"
    assert callable(test_audit_view), "审计日志装饰器应用失败"


def test_global_permission_functions():
    """测试全局权限函数"""
    from app.core.permissions import has_permission, has_role, get_user_permissions
    
    # 测试函数导入
    assert callable(has_permission), "has_permission函数导入失败"
    assert callable(has_role), "has_role函数导入失败"
    assert callable(get_user_permissions), "get_user_permissions函数导入失败"
    
    # 创建模拟用户测试
    mock_user = Mock()
    mock_user.is_superuser = True
    mock_user.is_active = True
    
    # 测试超级用户权限
    result = has_permission(mock_user, 'any:permission')
    assert result, "超级用户权限检查失败"


def test_permission_decorator_logic():
    """测试权限装饰器的逻辑（不依赖Flask上下文）"""
    from app.core.permissions import has_permission
    
    # 创建模拟用户
    admin_user = Mock()
    admin_user.is_superuser = False
    admin_user.is_active = True
    
    # 创建角色对象
    admin_role = Mock()
    admin_role.name = 'admin'
    admin_user.get_roles.return_value = [admin_role]
    
    # 测试管理员权限
    assert has_permission(admin_user, 'user:create'), "管理员应该有user:create权限"
    assert has_permission(admin_user, 'system:config'), "管理员应该有system:config权限"
    
    # 创建普通用户
    regular_user = Mock()
    regular_user.is_superuser = False
    regular_user.is_active = True
    
    user_role = Mock()
    user_role.name = 'user'
    regular_user.get_roles.return_value = [user_role]
    
    # 测试普通用户权限
    assert has_permission(regular_user, 'dashboard:view'), "普通用户应该有dashboard:view权限"
    assert not has_permission(regular_user, 'user:create'), "普通用户不应该有user:create权限"


def test_permission_combinations():
    """测试权限组合逻辑"""
    from app.core.permissions import has_permission
    
    # 创建有多个角色的用户
    multi_role_user = Mock()
    multi_role_user.is_superuser = False
    multi_role_user.is_active = True
    
    # 创建多个角色
    admin_role = Mock()
    admin_role.name = 'admin'
    manager_role = Mock()
    manager_role.name = 'manager'
    
    multi_role_user.get_roles.return_value = [admin_role, manager_role]
    
    # 测试多角色权限
    assert has_permission(multi_role_user, 'user:create'), "多角色用户应该有admin权限"
    assert has_permission(multi_role_user, 'dashboard:view'), "多角色用户应该有manager权限"


if __name__ == "__main__":
    print("开始修复的权限装饰器测试...")
    
    tests = [
        ("权限注册表", test_permission_registry),
        ("角色权限管理器", test_role_permission_manager),
        ("权限检查器", test_permission_checker),
        ("基础认证装饰器", test_basic_auth_decorators),
        ("高级权限装饰器", test_advanced_permission_decorators),
        ("全局权限函数", test_global_permission_functions),
        ("权限装饰器逻辑", test_permission_decorator_logic),
        ("权限组合逻辑", test_permission_combinations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"✓ {test_name} 测试通过")
        except Exception as e:
            print(f"✗ {test_name} 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有修复的权限装饰器测试通过！")
        sys.exit(0)
    else:
        print("❌ 存在问题，请检查上述错误信息")
        sys.exit(1)