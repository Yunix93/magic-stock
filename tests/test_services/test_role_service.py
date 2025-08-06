"""
角色权限服务测试

测试角色权限服务层的业务逻辑
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app.services.role_service import RoleService, role_service
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.core.exceptions import ValidationError, BusinessLogicError, DatabaseError


class TestRoleService:
    """角色服务测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.role_service = RoleService()
        self.sample_role_data = {
            'name': 'test_role',
            'description': 'Test Role Description',
            'is_active': True
        }
        self.sample_permission_data = {
            'name': 'test:permission',
            'resource': 'test',
            'action': 'permission',
            'description': 'Test Permission'
        }
    
    # ============================================================================
    # 角色创建测试
    # ==========================================