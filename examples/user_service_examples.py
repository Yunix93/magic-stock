#!/usr/bin/env python3
"""
用户服务使用示例

展示如何使用用户服务进行各种用户管理操作
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.user_service import user_service
from app.core.constants import UserStatus
from app.core.exceptions import ValidationError, BusinessLogicError


def example_create_user():
    """示例：创建用户"""
    print("=== 创建用户示例 ===")
    
    try:
        # 用户数据
        user_data = {
            'username': 'john_doe',
            'email': 'john.doe@example.com',
            'password': 'SecurePassword123',
            'full_name': 'John Doe',
            'phone': '+1234567890'
        }
        
        # 创建用户
        user = user_service.create_user(user_data, created_by='admin123')
        
        print(f"✓ 用户创建成功:")
        print(f"  ID: {user.id}")
        print(f"  用户名: {user.username}")
        print(f"  邮箱: {user.email}")
        print(f"  全名: {user.full_name}")
        print(f"  状态: {user.status}")
        print(f"  创建时间: {user.created_at}")
        
        return user.id
        
    except ValidationError as e:
        print(f"✗ 数据验证失败: {e}")
    except BusinessLogicError as e:
        print(f"✗ 业务逻辑错误: {e}")
    except Exception as e:
        print(f"✗ 创建用户失败: {e}")
    
    return None


def example_get_user():
    """示例：获取用户"""
    print("\\n=== 获取用户示例 ===")
    
    try:
        # 根据用户名获取用户
        user = user_service.get_user_by_username('john_doe')
        
        if user:
            print(f"✓ 用户信息:")
            print(f"  ID: {user.id}")
            print(f"  用户名: {user.username}")
            print(f"  邮箱: {user.email}")
            print(f"  全名: {user.full_name}")
            print(f"  电话: {user.phone}")
            print(f"  状态: {user.status}")
            print(f"  是否超级用户: {user.is_superuser}")
            print(f"  最后登录: {user.last_login_at}")
            
            return user.id
        else:
            print("✗ 用户不存在")
            
    except Exception as e:
        print(f"✗ 获取用户失败: {e}")
    
    return None


def example_update_user(user_id):
    """示例：更新用户"""
    print("\\n=== 更新用户示例 ===")
    
    if not user_id:
        print("✗ 需要有效的用户ID")
        return
    
    try:
        # 更新用户信息
        update_data = {
            'full_name': 'John Smith',
            'phone': '+1987654321'
        }
        
        updated_user = user_service.update_user(user_id, update_data, updated_by='admin123')
        
        print(f"✓ 用户更新成功:")
        print(f"  全名: {updated_user.full_name}")
        print(f"  电话: {updated_user.phone}")
        print(f"  更新时间: {updated_user.updated_at}")
        
    except BusinessLogicError as e:
        print(f"✗ 业务逻辑错误: {e}")
    except Exception as e:
        print(f"✗ 更新用户失败: {e}")


def example_user_profile_update(user_id):
    """示例：用户自己更新个人资料"""
    print("\\n=== 用户个人资料更新示例 ===")
    
    if not user_id:
        print("✗ 需要有效的用户ID")
        return
    
    try:
        # 用户只能更新特定字段
        profile_data = {
            'full_name': 'John Doe Smith',
            'phone': '+1555666777',
            'avatar_url': 'https://example.com/avatar.jpg',
            'username': 'hacker',  # 这个字段会被过滤掉
            'is_superuser': True   # 这个字段也会被过滤掉
        }
        
        updated_user = user_service.update_user_profile(user_id, profile_data)
        
        print(f"✓ 个人资料更新成功:")
        print(f"  全名: {updated_user.full_name}")
        print(f"  电话: {updated_user.phone}")
        print(f"  头像: {updated_user.avatar_url}")
        print(f"  用户名: {updated_user.username} (未被修改)")
        
    except Exception as e:
        print(f"✗ 个人资料更新失败: {e}")


def example_user_status_management(user_id):
    """示例：用户状态管理"""
    print("\\n=== 用户状态管理示例 ===")
    
    if not user_id:
        print("✗ 需要有效的用户ID")
        return
    
    try:
        # 停用用户
        print("1. 停用用户")
        deactivated_user = user_service.deactivate_user(user_id, 'admin123')
        print(f"   状态: {deactivated_user.status}")
        
        # 重新激活用户
        print("2. 激活用户")
        activated_user = user_service.activate_user(user_id, 'admin123')
        print(f"   状态: {activated_user.status}")
        
        # 锁定用户
        print("3. 锁定用户")
        locked_user = user_service.lock_user(user_id, 'admin123', '违规操作')
        print(f"   状态: {locked_user.status}")
        print(f"   锁定原因: {getattr(locked_user, 'lock_reason', '无')}")
        
        # 解锁用户
        print("4. 解锁用户")
        unlocked_user = user_service.unlock_user(user_id, 'admin123')
        print(f"   状态: {unlocked_user.status}")
        
    except Exception as e:
        print(f"✗ 用户状态管理失败: {e}")


def example_password_management(user_id):
    """示例：密码管理"""
    print("\\n=== 密码管理示例 ===")
    
    if not user_id:
        print("✗ 需要有效的用户ID")
        return
    
    try:
        # 用户修改密码
        print("1. 用户修改密码")
        success = user_service.change_password(
            user_id, 
            'SecurePassword123',  # 旧密码
            'NewSecurePassword456'  # 新密码
        )
        
        if success:
            print("   ✓ 密码修改成功")
        else:
            print("   ✗ 密码修改失败")
        
        # 管理员重置密码
        print("2. 管理员重置密码")
        new_password = user_service.reset_password(user_id, reset_by='admin123')
        print(f"   ✓ 密码重置成功，新密码: {new_password}")
        
    except BusinessLogicError as e:
        print(f"✗ 密码管理失败: {e}")
    except Exception as e:
        print(f"✗ 密码管理异常: {e}")


def example_user_list():
    """示例：获取用户列表"""
    print("\\n=== 用户列表示例 ===")
    
    try:
        # 获取用户列表（分页）
        print("1. 获取用户列表（第1页，每页5条）")
        users, total = user_service.get_users_list(page=1, per_page=5)
        
        print(f"   总用户数: {total}")
        print(f"   当前页用户数: {len(users)}")
        
        for i, user in enumerate(users, 1):
            print(f"   {i}. {user.username} ({user.email}) - {user.status}")
        
        # 搜索用户
        print("\\n2. 搜索用户（关键词: 'john'）")
        search_users, search_total = user_service.get_users_list(search='john')
        
        print(f"   搜索结果数: {search_total}")
        for user in search_users:
            print(f"   - {user.username} ({user.email})")
        
        # 按状态筛选
        print("\\n3. 筛选活跃用户")
        active_users, active_total = user_service.get_users_list(status=UserStatus.ACTIVE)
        
        print(f"   活跃用户数: {active_total}")
        
    except Exception as e:
        print(f"✗ 获取用户列表失败: {e}")


def example_role_management(user_id):
    """示例：用户角色管理"""
    print("\\n=== 用户角色管理示例 ===")
    
    if not user_id:
        print("✗ 需要有效的用户ID")
        return
    
    try:
        # 注意：这里假设已经有角色存在
        # 在实际使用中，需要先创建角色
        
        print("1. 为用户分配角色")
        # 假设有一个管理员角色
        role_assigned = user_service.assign_role_to_user(
            user_id, 
            'admin_role_id',  # 这需要是真实的角色ID
            'admin123'
        )
        
        if role_assigned:
            print("   ✓ 角色分配成功")
        
        print("2. 移除用户角色")
        role_removed = user_service.remove_role_from_user(
            user_id,
            'admin_role_id',
            'admin123'
        )
        
        if role_removed:
            print("   ✓ 角色移除成功")
        
    except BusinessLogicError as e:
        print(f"✗ 角色管理失败: {e}")
    except Exception as e:
        print(f"✗ 角色管理异常: {e}")


def example_user_statistics():
    """示例：用户统计"""
    print("\\n=== 用户统计示例 ===")
    
    try:
        stats = user_service.get_user_statistics()
        
        print("✓ 用户统计信息:")
        print(f"  总用户数: {stats.get('total_users', 0)}")
        print(f"  活跃用户数: {stats.get('active_users', 0)}")
        print(f"  超级用户数: {stats.get('superuser_count', 0)}")
        print(f"  最近注册数: {stats.get('recent_registrations', 0)}")
        print(f"  活跃率: {stats.get('activity_rate', 0)}%")
        
        print("\\n  状态分布:")
        status_dist = stats.get('status_distribution', {})
        for status, count in status_dist.items():
            print(f"    {status}: {count}")
        
    except Exception as e:
        print(f"✗ 获取用户统计失败: {e}")


def example_user_login_history(user_id):
    """示例：用户登录历史"""
    print("\\n=== 用户登录历史示例 ===")
    
    if not user_id:
        print("✗ 需要有效的用户ID")
        return
    
    try:
        login_history = user_service.get_user_login_history(user_id, limit=10)
        
        print(f"✓ 用户登录历史（最近10条）:")
        print(f"  记录数: {len(login_history)}")
        
        for i, log in enumerate(login_history, 1):
            print(f"  {i}. {log.login_time} - {log.status} - IP: {log.ip_address}")
        
    except Exception as e:
        print(f"✗ 获取登录历史失败: {e}")


def example_delete_user(user_id):
    """示例：删除用户"""
    print("\\n=== 删除用户示例 ===")
    
    if not user_id:
        print("✗ 需要有效的用户ID")
        return
    
    try:
        # 软删除用户
        print("1. 软删除用户")
        success = user_service.delete_user(user_id, 'admin123', soft_delete=True)
        
        if success:
            print("   ✓ 用户软删除成功")
        
        # 注意：硬删除会永久删除用户数据，请谨慎使用
        # print("2. 硬删除用户")
        # success = user_service.delete_user(user_id, 'admin123', soft_delete=False)
        
    except BusinessLogicError as e:
        print(f"✗ 删除用户失败: {e}")
    except Exception as e:
        print(f"✗ 删除用户异常: {e}")


def main():
    """主函数 - 运行所有示例"""
    print("用户服务使用示例")
    print("=" * 50)
    
    # 创建用户
    user_id = example_create_user()
    
    # 获取用户
    if not user_id:
        user_id = example_get_user()
    
    # 更新用户
    example_update_user(user_id)
    
    # 用户个人资料更新
    example_user_profile_update(user_id)
    
    # 用户状态管理
    example_user_status_management(user_id)
    
    # 密码管理
    example_password_management(user_id)
    
    # 用户列表
    example_user_list()
    
    # 角色管理
    example_role_management(user_id)
    
    # 用户统计
    example_user_statistics()
    
    # 登录历史
    example_user_login_history(user_id)
    
    # 删除用户（最后执行）
    example_delete_user(user_id)
    
    print("\\n" + "=" * 50)
    print("所有示例执行完成！")
    print("\\n注意事项:")
    print("- 这些示例需要在有效的数据库环境中运行")
    print("- 某些操作需要相应的权限和角色存在")
    print("- 实际使用时请根据业务需求调整参数")
    print("- 生产环境中请谨慎使用删除操作")


if __name__ == "__main__":
    main()