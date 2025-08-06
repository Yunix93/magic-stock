"""
用户服务测试

测试用户服务层的业务逻辑
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app.services.user_service import UserService, user_service
from app.models.user import User
from app.models.role import Role
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError
from app.core.constants import UserStatus


class TestUserService:
    """用户服务测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.user_service = UserService()
        self.sample_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'full_name': 'Test User'
        }
    
    # ============================================================================
    # 用户创建测试
    # ============================================================================
    
    @patch('app.services.user_service.get_db_session')
    @patch('app.services.user_service.hash_password')
    def test_create_user_success(self, mock_hash_password, mock_get_session):
        """测试成功创建用户"""
        # 模拟数据库会话
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟密码哈希
        mock_hash_password.return_value = 'hashed_password'
        
        # 模拟用户对象
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        
        # 模拟数据库操作
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        # 模拟唯一性检查
        with patch.object(self.user_service, '_check_user_uniqueness'):
            with patch.object(self.user_service, '_validate_user_creation_data', 
                            return_value=self.sample_user_data):
                with patch('app.services.user_service.User', return_value=mock_user):
                    result = self.user_service.create_user(self.sample_user_data, 'admin123')
                    
                    # 验证结果
                    assert result == mock_user
                    mock_session.add.assert_called_once()
                    mock_session.commit.assert_called_once()
    
    def test_create_user_validation_error(self):
        """测试创建用户时数据验证失败"""
        invalid_data = {
            'username': '',  # 空用户名
            'email': 'invalid-email',  # 无效邮箱
            'password': '123'  # 弱密码
        }
        
        with pytest.raises(ValidationError):
            self.user_service.create_user(invalid_data)
    
    @patch('app.services.user_service.get_db_session')
    def test_create_user_duplicate_username(self, mock_get_session):
        """测试创建用户时用户名重复"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟用户名已存在
        with patch.object(self.user_service, '_check_user_uniqueness', 
                         side_effect=BusinessLogicError("用户名已存在")):
            with pytest.raises(BusinessLogicError, match="用户名已存在"):
                self.user_service.create_user(self.sample_user_data)
    
    # ============================================================================
    # 用户查询测试
    # ============================================================================
    
    @patch('app.services.user_service.get_db_session')
    def test_get_user_by_id_success(self, mock_get_session):
        """测试根据ID获取用户成功"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟用户对象
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'testuser'
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_service.get_user_by_id('user123')
        
        assert result == mock_user
        mock_session.query.assert_called_once_with(User)
    
    @patch('app.services.user_service.get_db_session')
    def test_get_user_by_id_not_found(self, mock_get_session):
        """测试根据ID获取用户不存在"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_service.get_user_by_id('nonexistent')
        
        assert result is None
    
    @patch('app.services.user_service.get_db_session')
    def test_get_user_by_username_success(self, mock_get_session):
        """测试根据用户名获取用户成功"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = Mock()
        mock_user.username = 'testuser'
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_service.get_user_by_username('testuser')
        
        assert result == mock_user
    
    @patch('app.services.user_service.get_db_session')
    def test_get_users_list_with_pagination(self, mock_get_session):
        """测试获取用户列表（分页）"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟用户列表
        mock_users = [Mock(), Mock(), Mock()]
        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_users
        
        mock_session.query.return_value = mock_query
        
        users, total = self.user_service.get_users_list(page=1, per_page=3)
        
        assert users == mock_users
        assert total == 10
        mock_query.offset.assert_called_once_with(0)
        mock_query.offset.return_value.limit.assert_called_once_with(3)
    
    @patch('app.services.user_service.get_db_session')
    def test_get_users_list_with_search(self, mock_get_session):
        """测试获取用户列表（搜索）"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        
        mock_session.query.return_value = mock_query
        
        users, total = self.user_service.get_users_list(search='test')
        
        # 验证搜索过滤器被应用
        mock_query.filter.assert_called()
    
    # ============================================================================
    # 用户更新测试
    # ============================================================================
    
    @patch('app.services.user_service.get_db_session')
    def test_update_user_success(self, mock_get_session):
        """测试更新用户成功"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟现有用户
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'olduser'
        mock_user.email = 'old@example.com'
        mock_user.full_name = 'Old Name'
        mock_user.status = UserStatus.ACTIVE
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        update_data = {
            'full_name': 'New Name',
            'email': 'new@example.com'
        }
        
        with patch.object(self.user_service, '_validate_user_update_data', 
                         return_value=update_data):
            with patch.object(self.user_service, '_check_user_uniqueness'):
                result = self.user_service.update_user('user123', update_data, 'admin123')
                
                # 验证用户属性被更新
                assert mock_user.full_name == 'New Name'
                assert mock_user.email == 'new@example.com'
                assert result == mock_user
                mock_session.commit.assert_called_once()
    
    @patch('app.services.user_service.get_db_session')
    def test_update_user_not_found(self, mock_get_session):
        """测试更新不存在的用户"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(BusinessLogicError, match="用户不存在"):
            self.user_service.update_user('nonexistent', {'full_name': 'New Name'})
    
    def test_update_user_profile_filters_fields(self):
        """测试更新用户个人资料只允许特定字段"""
        profile_data = {
            'full_name': 'New Name',
            'phone': '1234567890',
            'avatar_url': 'http://example.com/avatar.jpg',
            'username': 'hacker',  # 不应该被更新
            'is_superuser': True   # 不应该被更新
        }
        
        with patch.object(self.user_service, 'update_user') as mock_update:
            self.user_service.update_user_profile('user123', profile_data)
            
            # 验证只有允许的字段被传递
            called_args = mock_update.call_args[0]
            called_kwargs = mock_update.call_args[1]
            
            filtered_data = called_args[1]
            assert 'full_name' in filtered_data
            assert 'phone' in filtered_data
            assert 'avatar_url' in filtered_data
            assert 'username' not in filtered_data
            assert 'is_superuser' not in filtered_data
    
    # ============================================================================
    # 用户状态管理测试
    # ============================================================================
    
    def test_activate_user(self):
        """测试激活用户"""
        with patch.object(self.user_service, 'update_user') as mock_update:
            mock_user = Mock()
            mock_update.return_value = mock_user
            
            result = self.user_service.activate_user('user123', 'admin123')
            
            mock_update.assert_called_once_with(
                'user123', 
                {'status': UserStatus.ACTIVE}, 
                updated_by='admin123'
            )
            assert result == mock_user
    
    def test_deactivate_user(self):
        """测试停用用户"""
        with patch.object(self.user_service, 'update_user') as mock_update:
            mock_user = Mock()
            mock_update.return_value = mock_user
            
            result = self.user_service.deactivate_user('user123', 'admin123')
            
            mock_update.assert_called_once_with(
                'user123', 
                {'status': UserStatus.INACTIVE}, 
                updated_by='admin123'
            )
            assert result == mock_user
    
    def test_lock_user_with_reason(self):
        """测试锁定用户（带原因）"""
        with patch.object(self.user_service, 'update_user') as mock_update:
            mock_user = Mock()
            mock_update.return_value = mock_user
            
            result = self.user_service.lock_user('user123', 'admin123', '违规操作')
            
            mock_update.assert_called_once_with(
                'user123', 
                {'status': UserStatus.LOCKED, 'lock_reason': '违规操作'}, 
                updated_by='admin123'
            )
            assert result == mock_user
    
    def test_unlock_user(self):
        """测试解锁用户"""
        with patch.object(self.user_service, 'update_user') as mock_update:
            mock_user = Mock()
            mock_update.return_value = mock_user
            
            result = self.user_service.unlock_user('user123', 'admin123')
            
            mock_update.assert_called_once_with(
                'user123', 
                {'status': UserStatus.ACTIVE, 'lock_reason': None}, 
                updated_by='admin123'
            )
            assert result == mock_user
    
    # ============================================================================
    # 密码管理测试
    # ============================================================================
    
    @patch('app.services.user_service.get_db_session')
    @patch('app.services.user_service.verify_password')
    @patch('app.services.user_service.hash_password')
    def test_change_password_success(self, mock_hash_password, mock_verify_password, mock_get_session):
        """测试修改密码成功"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟用户
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'testuser'
        mock_user.password_hash = 'old_hash'
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # 模拟密码验证和哈希
        mock_verify_password.return_value = True
        mock_hash_password.return_value = 'new_hash'
        
        result = self.user_service.change_password('user123', 'old_password', 'new_password')
        
        assert result is True
        assert mock_user.password_hash == 'new_hash'
        mock_session.commit.assert_called_once()
    
    @patch('app.services.user_service.get_db_session')
    @patch('app.services.user_service.verify_password')
    def test_change_password_wrong_old_password(self, mock_verify_password, mock_get_session):
        """测试修改密码时旧密码错误"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # 模拟旧密码验证失败
        mock_verify_password.return_value = False
        
        with pytest.raises(BusinessLogicError, match="原密码不正确"):
            self.user_service.change_password('user123', 'wrong_password', 'new_password')
    
    @patch('app.services.user_service.get_db_session')
    @patch('app.services.user_service.generate_secure_token')
    @patch('app.services.user_service.hash_password')
    def test_reset_password_auto_generate(self, mock_hash_password, mock_generate_token, mock_get_session):
        """测试重置密码（自动生成）"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'testuser'
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # 模拟生成新密码
        mock_generate_token.return_value = 'generated_password'
        mock_hash_password.return_value = 'new_hash'
        
        result = self.user_service.reset_password('user123', reset_by='admin123')
        
        assert result == 'generated_password'
        assert mock_user.password_hash == 'new_hash'
        mock_session.commit.assert_called_once()
    
    # ============================================================================
    # 用户删除测试
    # ============================================================================
    
    @patch('app.services.user_service.get_db_session')
    def test_delete_user_soft_delete(self, mock_get_session):
        """测试软删除用户"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'testuser'
        mock_user.is_superuser = False
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_service.delete_user('user123', 'admin123', soft_delete=True)
        
        assert result is True
        assert mock_user.status == UserStatus.DELETED
        assert mock_user.deleted_by == 'admin123'
        mock_session.commit.assert_called_once()
    
    @patch('app.services.user_service.get_db_session')
    def test_delete_user_hard_delete(self, mock_get_session):
        """测试硬删除用户"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'testuser'
        mock_user.is_superuser = False
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_service.delete_user('user123', 'admin123', soft_delete=False)
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_user)
        mock_session.commit.assert_called_once()
    
    @patch('app.services.user_service.get_db_session')
    def test_delete_superuser_protection(self, mock_get_session):
        """测试超级用户删除保护"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'superuser'
        mock_user.is_superuser = True
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        with patch.object(self.user_service, '_can_delete_superuser', return_value=False):
            with pytest.raises(BusinessLogicError, match="无法删除超级管理员用户"):
                self.user_service.delete_user('user123', 'admin123')
    
    # ============================================================================
    # 用户角色管理测试
    # ============================================================================
    
    @patch('app.services.user_service.get_db_session')
    def test_assign_role_to_user_success(self, mock_get_session):
        """测试为用户分配角色成功"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟用户和角色
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'testuser'
        mock_user.roles = []
        
        mock_role = Mock()
        mock_role.id = 'role123'
        mock_role.name = 'admin'
        
        mock_session.query.side_effect = lambda model: {
            User: Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_user)))),
            Role: Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_role))))
        }[model]
        
        result = self.user_service.assign_role_to_user('user123', 'role123', 'admin123')
        
        assert result is True
        mock_user.roles.append.assert_called_once_with(mock_role)
        mock_session.commit.assert_called_once()
    
    @patch('app.services.user_service.get_db_session')
    def test_assign_role_user_not_found(self, mock_get_session):
        """测试为不存在的用户分配角色"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(BusinessLogicError, match="用户不存在"):
            self.user_service.assign_role_to_user('nonexistent', 'role123')
    
    @patch('app.services.user_service.get_db_session')
    def test_remove_role_from_user_success(self, mock_get_session):
        """测试移除用户角色成功"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟用户和角色
        mock_role = Mock()
        mock_role.id = 'role123'
        mock_role.name = 'admin'
        
        mock_user = Mock()
        mock_user.id = 'user123'
        mock_user.username = 'testuser'
        mock_user.roles = [mock_role]
        
        mock_session.query.side_effect = lambda model: {
            User: Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_user)))),
            Role: Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_role))))
        }[model]
        
        result = self.user_service.remove_role_from_user('user123', 'role123', 'admin123')
        
        assert result is True
        mock_user.roles.remove.assert_called_once_with(mock_role)
        mock_session.commit.assert_called_once()
    
    # ============================================================================
    # 用户统计测试
    # ============================================================================
    
    @patch('app.services.user_service.get_db_session')
    def test_get_user_statistics(self, mock_get_session):
        """测试获取用户统计信息"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟查询结果
        mock_query = Mock()
        mock_query.count.side_effect = [100, 80, 80, 10, 5, 5, 20, 15]  # 各种统计数据
        mock_query.filter.return_value = mock_query
        
        mock_session.query.return_value = mock_query
        
        stats = self.user_service.get_user_statistics()
        
        assert 'total_users' in stats
        assert 'active_users' in stats
        assert 'status_distribution' in stats
        assert 'superuser_count' in stats
        assert 'recent_registrations' in stats
        assert 'activity_rate' in stats
    
    @patch('app.models.logs.LoginLog.get_by_user')
    def test_get_user_login_history(self, mock_get_by_user):
        """测试获取用户登录历史"""
        mock_logs = [Mock(), Mock(), Mock()]
        mock_get_by_user.return_value = mock_logs
        
        result = self.user_service.get_user_login_history('user123', 10)
        
        assert result == mock_logs
        mock_get_by_user.assert_called_once_with('user123', 10)
    
    # ============================================================================
    # 私有方法测试
    # ============================================================================
    
    def test_validate_user_creation_data_success(self):
        """测试用户创建数据验证成功"""
        with patch('app.services.user_service.username_validator') as mock_username_validator:
            with patch('app.services.user_service.email_validator') as mock_email_validator:
                with patch('app.services.user_service.password_validator') as mock_password_validator:
                    # 模拟验证器
                    mock_username_validator.validate.return_value = 'testuser'
                    mock_email_validator.validate.return_value = 'test@example.com'
                    mock_password_validator.validate.return_value = 'TestPassword123'
                    
                    result = self.user_service._validate_user_creation_data(self.sample_user_data)
                    
                    assert result['username'] == 'testuser'
                    assert result['email'] == 'test@example.com'
                    assert result['password'] == 'TestPassword123'
                    assert result['full_name'] == 'Test User'
    
    def test_validate_user_creation_data_missing_field(self):
        """测试用户创建数据验证缺少必需字段"""
        incomplete_data = {
            'username': 'testuser',
            # 缺少email和password
        }
        
        with pytest.raises(ValidationError, match="缺少必需字段"):
            self.user_service._validate_user_creation_data(incomplete_data)
    
    @patch('app.services.user_service.get_db_session')
    def test_check_user_uniqueness_username_exists(self, mock_get_session):
        """测试检查用户名唯一性 - 用户名已存在"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟用户名已存在
        mock_session.query.return_value.filter.return_value.first.return_value = Mock()
        
        with pytest.raises(BusinessLogicError, match="用户名已存在"):
            self.user_service._check_user_uniqueness(username='existinguser')
    
    @patch('app.services.user_service.get_db_session')
    def test_check_user_uniqueness_email_exists(self, mock_get_session):
        """测试检查邮箱唯一性 - 邮箱已存在"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟邮箱已存在
        mock_session.query.return_value.filter.return_value.first.return_value = Mock()
        
        with pytest.raises(BusinessLogicError, match="邮箱已存在"):
            self.user_service._check_user_uniqueness(email='existing@example.com')
    
    @patch('app.services.user_service.get_db_session')
    def test_can_delete_superuser_not_superuser_deleter(self, mock_get_session):
        """测试非超级用户不能删除超级用户"""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # 模拟删除者不是超级用户
        mock_deleter = Mock()
        mock_deleter.is_superuser = False
        mock_session.query.return_value.filter.return_value.first.return_value = mock_deleter
        
        result = self.user_service._can_delete_superuser('user123', 'deleter123')
        
        assert result is False
    
    @patch('app.services.user_service.get_db_session')
    def test_can_delete_superuser_self_deletion(self, mock_get_session):
        """测试超级用户不能删除自己"""
        result = self.user_service._can_delete_superuser('user123', 'user123')
        
        assert result is False


class TestUserServiceGlobalInstance:
    """测试全局用户服务实例"""
    
    def test_global_user_service_instance(self):
        """测试全局用户服务实例存在"""
        assert user_service is not None
        assert isinstance(user_service, UserService)
    
    def test_global_user_service_methods(self):
        """测试全局用户服务实例方法存在"""
        assert hasattr(user_service, 'create_user')
        assert hasattr(user_service, 'get_user_by_id')
        assert hasattr(user_service, 'update_user')
        assert hasattr(user_service, 'delete_user')
        assert hasattr(user_service, 'change_password')
        assert hasattr(user_service, 'assign_role_to_user')


if __name__ == '__main__':
    pytest.main([__file__])