#!/usr/bin/env python3
"""
用户服务简化测试

测试用户服务的核心功能，避免数据库依赖
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.user_service import UserService, user_service
from app.core.constants import UserStatus
from app.core.exceptions import ValidationError, BusinessLogicError


def test_user_service_initialization():
    """测试用户服务初始化"""
    print("=== 测试用户服务初始化 ===")
    
    # 测试创建用户服务实例
    service = UserService()
    assert service is not None
    print("✓ 用户服务实例创建成功")
    
    # 测试全局用户服务实例
    assert user_service is not None
    assert isinstance(user_service, UserService)
    print("✓ 全局用户服务实例存在")
    
    return True


def test_user_service_methods():
    """测试用户服务方法存在"""
    print("\n=== 测试用户服务方法 ===")
    
    service = UserService()
    
    # 检查核心方法存在
    methods = [
        'create_user', 'get_user_by_id', 'get_user_by_username', 
        'get_user_by_email', 'get_users_list', 'update_user',
        'activate_user', 'deactivate_user', 'lock_user', 'unlock_user',
        'change_password', 'reset_password', 'delete_user',
        'assign_role_to_user', 'remove_role_from_user',
        'get_user_statistics', 'get_user_login_history'
    ]
    
    for method in methods:
        assert hasattr(service, method), f"方法 {method} 不存在"
        assert callable(getattr(service, method)), f"方法 {method} 不可调用"
    
    print(f"✓ 所有 {len(methods)} 个核心方法存在且可调用")
    
    return True


def test_user_validation_methods():
    """测试用户数据验证方法"""
    print("\n=== 测试用户数据验证 ===")
    
    service = UserService()
    
    # 测试用户创建数据验证
    try:
        # 测试缺少必需字段
        invalid_data = {'username': 'test'}  # 缺少email和password
        service._validate_user_creation_data(invalid_data)
        assert False, "应该抛出ValidationError"
    except ValidationError as e:
        assert "缺少必需字段" in str(e)
        print("✓ 缺少必需字段验证正常")
    
    # 测试有效数据验证（需要模拟验证器）
    with patch('app.services.user_service.username_validator') as mock_username:
        with patch('app.services.user_service.email_validator') as mock_email:
            with patch('app.services.user_service.password_validator') as mock_password:
                # 模拟验证器返回值
                mock_username.validate.return_value = 'testuser'
                mock_email.validate.return_value = 'test@example.com'
                mock_password.validate.return_value = 'TestPassword123'
                
                valid_data = {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'TestPassword123',
                    'full_name': 'Test User'
                }
                
                result = service._validate_user_creation_data(valid_data)
                
                assert result['username'] == 'testuser'
                assert result['email'] == 'test@example.com'
                assert result['password'] == 'TestPassword123'
                assert result['full_name'] == 'Test User'
                
                print("✓ 有效数据验证正常")
    
    return True


def test_user_status_management():
    """测试用户状态管理方法"""
    print("\n=== 测试用户状态管理 ===")
    
    service = UserService()
    
    # 模拟update_user方法
    with patch.object(service, 'update_user') as mock_update:
        mock_user = Mock()
        mock_update.return_value = mock_user
        
        # 测试激活用户
        result = service.activate_user('user123', 'admin123')
        mock_update.assert_called_with(
            'user123', 
            {'status': UserStatus.ACTIVE}, 
            updated_by='admin123'
        )
        assert result == mock_user
        print("✓ 激活用户方法正常")
        
        # 测试停用用户
        result = service.deactivate_user('user123', 'admin123')
        mock_update.assert_called_with(
            'user123', 
            {'status': UserStatus.INACTIVE}, 
            updated_by='admin123'
        )
        assert result == mock_user
        print("✓ 停用用户方法正常")
        
        # 测试锁定用户
        result = service.lock_user('user123', 'admin123', '违规操作')
        mock_update.assert_called_with(
            'user123', 
            {'status': UserStatus.LOCKED, 'lock_reason': '违规操作'}, 
            updated_by='admin123'
        )
        assert result == mock_user
        print("✓ 锁定用户方法正常")
        
        # 测试解锁用户
        result = service.unlock_user('user123', 'admin123')
        mock_update.assert_called_with(
            'user123', 
            {'status': UserStatus.ACTIVE, 'lock_reason': None}, 
            updated_by='admin123'
        )
        assert result == mock_user
        print("✓ 解锁用户方法正常")
    
    return True


def test_user_profile_update():
    """测试用户个人资料更新"""
    print("\n=== 测试用户个人资料更新 ===")
    
    service = UserService()
    
    # 模拟update_user方法
    with patch.object(service, 'update_user') as mock_update:
        mock_user = Mock()
        mock_update.return_value = mock_user
        
        # 测试个人资料更新字段过滤
        profile_data = {
            'full_name': 'New Name',
            'phone': '1234567890',
            'avatar_url': 'http://example.com/avatar.jpg',
            'username': 'hacker',  # 不应该被更新
            'is_superuser': True   # 不应该被更新
        }
        
        result = service.update_user_profile('user123', profile_data)
        
        # 检查调用参数
        call_args = mock_update.call_args
        filtered_data = call_args[0][1]  # 第二个参数是更新数据
        
        # 验证只有允许的字段被传递
        assert 'full_name' in filtered_data
        assert 'phone' in filtered_data
        assert 'avatar_url' in filtered_data
        assert 'username' not in filtered_data
        assert 'is_superuser' not in filtered_data
        
        print("✓ 个人资料更新字段过滤正常")
    
    return True


def test_uniqueness_check():
    """测试用户唯一性检查"""
    print("\n=== 测试用户唯一性检查 ===")
    
    service = UserService()
    
    # 模拟数据库会话
    with patch('app.services.user_service.get_db_session') as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 测试用户名已存在
        mock_session.query.return_value.filter.return_value.first.return_value = Mock()
        
        try:
            service._check_user_uniqueness(username='existing_user')
            assert False, "应该抛出BusinessLogicError"
        except BusinessLogicError as e:
            assert "用户名已存在" in str(e)
            print("✓ 用户名唯一性检查正常")
        
        # 测试邮箱已存在
        try:
            service._check_user_uniqueness(email='existing@example.com')
            assert False, "应该抛出BusinessLogicError"
        except BusinessLogicError as e:
            assert "邮箱已存在" in str(e)
            print("✓ 邮箱唯一性检查正常")
        
        # 测试唯一性检查通过
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # 不应该抛出异常
        service._check_user_uniqueness(username='new_user', email='new@example.com')
        print("✓ 唯一性检查通过正常")
    
    return True


def test_superuser_deletion_check():
    """测试超级用户删除检查"""
    print("\n=== 测试超级用户删除检查 ===")
    
    service = UserService()
    
    # 测试非超级用户不能删除超级用户
    with patch('app.services.user_service.get_db_session') as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟删除者不是超级用户
        mock_deleter = Mock()
        mock_deleter.is_superuser = False
        mock_session.query.return_value.filter.return_value.first.return_value = mock_deleter
        
        result = service._can_delete_superuser('user123', 'deleter123')
        assert result is False
        print("✓ 非超级用户不能删除超级用户")
        
        # 测试不能删除自己
        result = service._can_delete_superuser('user123', 'user123')
        assert result is False
        print("✓ 不能删除自己")
    
    return True


def test_user_constants():
    """测试用户相关常量"""
    print("\n=== 测试用户相关常量 ===")
    
    # 测试用户状态常量
    assert UserStatus.ACTIVE.value == "active"
    assert UserStatus.INACTIVE.value == "inactive"
    assert UserStatus.LOCKED.value == "locked"
    assert UserStatus.DELETED.value == "deleted"
    
    print("✓ 用户状态常量定义正确")
    
    return True


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    service = UserService()
    
    # 测试ValidationError处理
    try:
        service._validate_user_creation_data({})
        assert False, "应该抛出ValidationError"
    except ValidationError:
        print("✓ ValidationError处理正常")
    
    # 测试BusinessLogicError处理
    with patch('app.services.user_service.get_db_session') as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟用户名已存在
        mock_session.query.return_value.filter.return_value.first.return_value = Mock()
        
        try:
            service._check_user_uniqueness(username='existing')
            assert False, "应该抛出BusinessLogicError"
        except BusinessLogicError:
            print("✓ BusinessLogicError处理正常")
    
    return True


def main():
    """主测试函数"""
    print("用户服务简化测试")
    print("=" * 50)
    
    tests = [
        ("用户服务初始化", test_user_service_initialization),
        ("用户服务方法", test_user_service_methods),
        ("用户数据验证", test_user_validation_methods),
        ("用户状态管理", test_user_status_management),
        ("用户个人资料更新", test_user_profile_update),
        ("用户唯一性检查", test_uniqueness_check),
        ("超级用户删除检查", test_superuser_deletion_check),
        ("用户相关常量", test_user_constants),
        ("错误处理", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 测试通过\n")
            else:
                print(f"✗ {test_name} 测试失败\n")
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有用户服务测试通过！")
        print("✅ 用户服务核心功能正常")
        print("✅ 数据验证功能正常")
        print("✅ 状态管理功能正常")
        print("✅ 错误处理功能正常")
        return True
    else:
        print("❌ 存在问题，请检查上述错误信息")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)