#!/usr/bin/env python3
"""
角色权限服务使用示例

展示如何使用角色权限服务进行各种角色和权限管理操作
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.role_service import role_service
from app.core.exceptions import ValidationError, BusinessLogicError


def example_create_role():
    """示例：创建角色"""
    print("=== 创建角色示例 ===")
    
    try:
        # 角色数据
        role_data = {
            'name': 'project_manager',
            'description': '项目经理角色，负责项目管理相关工作',
            'is_active': True,
            'sort_order': '5'
        }
        
        # 创建角色
        role = role_service.create_role(role_data, created_by='admin123')
        
        print(f"✓ 角色创建成功:")
        print(f"  ID: {role.id}")
        print(f"  名称: {role.name}")
        print(f"  描述: {role.description}")
        print(f"  状态: {'激活' if role.is_active else '停用'}")
        print(f"  创建时间: {role.created_at}")
        
        return role.id
        
    except ValidationError as e:
        print(f"✗ 数据验证失败: {e}")
    except BusinessLogicError as e:
        print(f"✗ 业务逻辑错误: {e}")
    except Exception as e:
        print(f"✗ 创建角色失败: {e}")
    
    return None


def example_create_permission():
    """示例：创建权限"""
    print("\\n=== 创建权限示例 ===")
    
    try:
        # 权限数据
        permission_data = {
            'name': 'project:manage',
            'resource': 'project',
            'action': 'manage',
            'description': '项目管理权限，包括创建、编辑、删除项目',
            'group': '项目管理'
        }
        
        # 创建权限
        permission = role_service.create_permission(permission_data, created_by='admin123')
        
        print(f"✓ 权限创建成功:")
        print(f"  ID: {permission.id}")
        print(f"  名称: {permission.name}")
        print(f"  资源: {permission.resource}")
        print(f"  操作: {permission.action}")
        print(f"  描述: {permission.description}")
        print(f"  分组: {permission.group}")
        
        return permission.id
        
    except ValidationError as e:
        print(f"✗ 数据验证失败: {e}")
    except BusinessLogicError as e:
        print(f"✗ 业务逻辑错误: {e}")
    except Exception as e:
        print(f"✗ 创建权限失败: {e}")
    
    return None


def example_get_role():
    """示例：获取角色"""
    print("\\n=== 获取角色示例 ===")
    
    try:
        # 根据名称获取角色
        role = role_service.get_role_by_name('project_manager')
        
        if role:
            print(f"✓ 角色信息:")
            print(f"  ID: {role.id}")
            print(f"  名称: {role.name}")
            print(f"  描述: {role.description}")
            print(f"  状态: {'激活' if role.is_active else '停用'}")
            print(f"  是否系统角色: {'是' if role.is_system else '否'}")
            print(f"  排序: {role.sort_order}")
            
            return role.id
        else:
            print("✗ 角色不存在")
            
    except Exception as e:
        print(f"✗ 获取角色失败: {e}")
    
    return None


def example_assign_permission_to_role(role_id, permission_id):
    """示例：为角色分配权限"""
    print("\\n=== 角色权限分配示例 ===")
    
    if not role_id or not permission_id:
        print("✗ 需要有效的角色ID和权限ID")
        return
    
    try:
        # 为角色分配权限
        success = role_service.assign_permission_to_role(
            role_id, 
            permission_id, 
            assigned_by='admin123'
        )
        
        if success:
            print("✓ 权限分配成功")
            
            # 获取角色权限列表
            permissions = role_service.get_role_permissions(role_id)
            print(f"  角色当前权限数量: {len(permissions)}")
            for perm in permissions:
                print(f"    - {perm.name}: {perm.description}")
        else:
            print("✗ 权限分配失败")
            
    except BusinessLogicError as e:
        print(f"✗ 业务逻辑错误: {e}")
    except Exception as e:
        print(f"✗ 权限分配异常: {e}")


def example_batch_assign_permissions():
    """示例：批量权限分配"""
    print("\\n=== 批量权限分配示例 ===")
    
    try:
        # 首先创建一些测试权限
        test_permissions = [
            {'name': 'project:create', 'resource': 'project', 'action': 'create', 'description': '创建项目'},
            {'name': 'project:read', 'resource': 'project', 'action': 'read', 'description': '查看项目'},
            {'name': 'project:update', 'resource': 'project', 'action': 'update', 'description': '更新项目'},
            {'name': 'project:delete', 'resource': 'project', 'action': 'delete', 'description': '删除项目'},
        ]
        
        permission_ids = []
        for perm_data in test_permissions:
            try:
                permission = role_service.create_permission(perm_data, created_by='admin123')
                permission_ids.append(permission.id)
                print(f"  创建权限: {permission.name}")
            except BusinessLogicError:
                # 权限可能已存在，尝试获取
                existing_perm = role_service.get_permission_by_name(perm_data['name'])
                if existing_perm:
                    permission_ids.append(existing_perm.id)
                    print(f"  使用现有权限: {existing_perm.name}")
        
        # 创建测试角色
        try:
            role = role_service.create_role({
                'name': 'project_admin',
                'description': '项目管理员，拥有项目相关的所有权限'
            }, created_by='admin123')
            role_id = role.id
            print(f"  创建角色: {role.name}")
        except BusinessLogicError:
            # 角色可能已存在
            existing_role = role_service.get_role_by_name('project_admin')
            if existing_role:
                role_id = existing_role.id
                print(f"  使用现有角色: {existing_role.name}")
            else:
                print("✗ 无法创建或获取测试角色")
                return
        
        # 批量分配权限
        result = role_service.batch_assign_permissions_to_role(
            role_id, 
            permission_ids, 
            assigned_by='admin123'
        )
        
        print(f"✓ 批量权限分配完成:")
        print(f"  总权限数: {result['total']}")
        print(f"  成功分配: {result['success']}")
        print(f"  已存在: {result['already_exists']}")
        print(f"  失败: {result['failed']}")
        
        if result['failed_permissions']:
            print(f"  失败的权限: {result['failed_permissions']}")
        
    except Exception as e:
        print(f"✗ 批量权限分配失败: {e}")


def example_role_list():
    """示例：获取角色列表"""
    print("\\n=== 角色列表示例 ===")
    
    try:
        # 获取角色列表（分页）
        print("1. 获取角色列表（第1页，每页5条）")
        roles, total = role_service.get_roles_list(page=1, per_page=5)
        
        print(f"   总角色数: {total}")
        print(f"   当前页角色数: {len(roles)}")
        
        for i, role in enumerate(roles, 1):
            status = "激活" if role.is_active else "停用"
            system = "系统" if role.is_system else "自定义"
            print(f"   {i}. {role.name} ({role.description}) - {status} - {system}")
        
        # 搜索角色
        print("\\n2. 搜索角色（关键词: 'admin'）")
        search_roles, search_total = role_service.get_roles_list(search='admin')
        
        print(f"   搜索结果数: {search_total}")
        for role in search_roles:
            print(f"   - {role.name}: {role.description}")
        
        # 筛选系统角色
        print("\\n3. 筛选系统角色")
        system_roles, system_total = role_service.get_roles_list(is_system=True)
        
        print(f"   系统角色数: {system_total}")
        for role in system_roles:
            print(f"   - {role.name}: {role.description}")
        
    except Exception as e:
        print(f"✗ 获取角色列表失败: {e}")


def example_permission_list():
    """示例：获取权限列表"""
    print("\\n=== 权限列表示例 ===")
    
    try:
        # 获取权限列表（分页）
        print("1. 获取权限列表（第1页，每页10条）")
        permissions, total = role_service.get_permissions_list(page=1, per_page=10)
        
        print(f"   总权限数: {total}")
        print(f"   当前页权限数: {len(permissions)}")
        
        for i, perm in enumerate(permissions, 1):
            print(f"   {i}. {perm.name} ({perm.resource}:{perm.action}) - {perm.description}")
        
        # 按资源筛选
        print("\\n2. 筛选项目相关权限")
        project_perms, project_total = role_service.get_permissions_list(resource='project')
        
        print(f"   项目权限数: {project_total}")
        for perm in project_perms:
            print(f"   - {perm.name}: {perm.description}")
        
        # 按分组筛选
        print("\\n3. 筛选用户管理权限")
        user_perms, user_total = role_service.get_permissions_list(group='用户管理')
        
        print(f"   用户管理权限数: {user_total}")
        for perm in user_perms:
            print(f"   - {perm.name}: {perm.description}")
        
    except Exception as e:
        print(f"✗ 获取权限列表失败: {e}")


def example_user_permission_check():
    """示例：用户权限检查"""
    print("\\n=== 用户权限检查示例 ===")
    
    try:
        # 模拟用户ID（在实际使用中应该是真实的用户ID）
        user_id = 'user123'
        
        # 检查用户是否有特定权限
        print("1. 检查用户权限")
        has_user_create = role_service.check_user_permission(user_id, 'user:create')
        has_project_manage = role_service.check_user_permission(user_id, 'project:manage')
        
        print(f"   用户是否有 user:create 权限: {'是' if has_user_create else '否'}")
        print(f"   用户是否有 project:manage 权限: {'是' if has_project_manage else '否'}")
        
        # 获取用户所有权限
        print("\\n2. 获取用户所有权限")
        user_permissions = role_service.get_user_permissions(user_id)
        
        print(f"   用户权限总数: {len(user_permissions)}")
        for perm in user_permissions[:5]:  # 只显示前5个
            print(f"   - {perm.name}: {perm.description}")
        
        if len(user_permissions) > 5:
            print(f"   ... 还有 {len(user_permissions) - 5} 个权限")
        
        # 获取用户角色及权限详情
        print("\\n3. 获取用户角色及权限详情")
        user_roles_info = role_service.get_user_roles_with_permissions(user_id)
        
        print(f"   用户角色数: {len(user_roles_info.get('roles', []))}")
        print(f"   总权限数: {user_roles_info.get('total_permissions', 0)}")
        
        for role_info in user_roles_info.get('roles', [])[:3]:  # 只显示前3个角色
            print(f"   角色: {role_info['name']} - 权限数: {len(role_info['permissions'])}")
        
    except Exception as e:
        print(f"✗ 用户权限检查失败: {e}")


def example_role_statistics():
    """示例：角色统计"""
    print("\\n=== 角色统计示例 ===")
    
    try:
        stats = role_service.get_role_statistics()
        
        print("✓ 角色统计信息:")
        print(f"  总角色数: {stats.get('total_roles', 0)}")
        print(f"  激活角色数: {stats.get('active_roles', 0)}")
        print(f"  系统角色数: {stats.get('system_roles', 0)}")
        print(f"  自定义角色数: {stats.get('custom_roles', 0)}")
        
        print("\\n  角色分布:")
        role_distribution = stats.get('role_distribution', {})
        for status, count in role_distribution.items():
            print(f"    {status}: {count}")
        
    except Exception as e:
        print(f"✗ 获取角色统计失败: {e}")


def example_permission_statistics():
    """示例：权限统计"""
    print("\\n=== 权限统计示例 ===")
    
    try:
        stats = role_service.get_permission_statistics()
        
        print("✓ 权限统计信息:")
        print(f"  总权限数: {stats.get('total_permissions', 0)}")
        print(f"  已分配权限数: {stats.get('assigned_permissions', 0)}")
        print(f"  未分配权限数: {stats.get('unassigned_permissions', 0)}")
        
        print("\\n  权限分组分布:")
        group_distribution = stats.get('group_distribution', {})
        for group, count in group_distribution.items():
            print(f"    {group}: {count}")
        
        print("\\n  资源分布:")
        resource_distribution = stats.get('resource_distribution', {})
        for resource, count in resource_distribution.items():
            print(f"    {resource}: {count}")
        
    except Exception as e:
        print(f"✗ 获取权限统计失败: {e}")


def example_update_role(role_id):
    """示例：更新角色"""
    print("\\n=== 更新角色示例 ===")
    
    if not role_id:
        print("✗ 需要有效的角色ID")
        return
    
    try:
        # 更新角色信息
        update_data = {
            'description': '项目经理角色 - 已更新描述',
            'sort_order': '10'
        }
        
        updated_role = role_service.update_role(role_id, update_data, updated_by='admin123')
        
        print(f"✓ 角色更新成功:")
        print(f"  名称: {updated_role.name}")
        print(f"  描述: {updated_role.description}")
        print(f"  排序: {updated_role.sort_order}")
        print(f"  更新时间: {updated_role.updated_at}")
        
    except BusinessLogicError as e:
        print(f"✗ 业务逻辑错误: {e}")
    except Exception as e:
        print(f"✗ 更新角色失败: {e}")


def main():
    """主函数 - 运行所有示例"""
    print("角色权限服务使用示例")
    print("=" * 50)
    
    # 创建角色和权限
    role_id = example_create_role()
    permission_id = example_create_permission()
    
    # 获取角色
    if not role_id:
        role_id = example_get_role()
    
    # 权限分配
    example_assign_permission_to_role(role_id, permission_id)
    
    # 批量权限分配
    example_batch_assign_permissions()
    
    # 列表查询
    example_role_list()
    example_permission_list()
    
    # 用户权限检查
    example_user_permission_check()
    
    # 统计信息
    example_role_statistics()
    example_permission_statistics()
    
    # 更新角色
    example_update_role(role_id)
    
    print("\\n" + "=" * 50)
    print("所有示例执行完成！")
    print("\\n注意事项:")
    print("- 这些示例需要在有效的数据库环境中运行")
    print("- 某些操作需要相应的权限和数据存在")
    print("- 实际使用时请根据业务需求调整参数")
    print("- 生产环境中请谨慎使用删除操作")


if __name__ == "__main__":
    main()