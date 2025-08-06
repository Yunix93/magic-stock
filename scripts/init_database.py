#!/usr/bin/env python3
"""
数据库初始化脚本

创建数据库表结构并初始化基础数据
"""

import os
import sys
from datetime import datetime, timezone

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import script_utils, print_header, print_footer, print_admin_info

def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    try:
        # 使用统一的应用初始化
        app, server = script_utils.init_app_context()
        
        with server.app_context():
            # 初始化数据库连接
            engine, session = script_utils.init_database_connection()
            
            # 创建所有表
            print("📋 创建数据库表...")
            if not script_utils.create_database_tables():
                return False
            
            # 初始化基础数据
            print("📊 初始化基础数据...")
            init_basic_data()
            print("✅ 基础数据初始化完成")
            
            print("🎉 数据库初始化成功！")
            return True
            
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def init_basic_data():
    """初始化基础数据"""
    # 初始化权限数据
    init_permissions()
    
    # 初始化角色数据
    init_roles()
    
    # 初始化管理员用户
    init_admin_user()


def init_permissions():
    """初始化基础权限数据"""
    from app.services.permission_service import permission_service
    
    print("  创建基础权限...")
    
    # 定义基础权限
    permissions = [
        # 用户管理权限
        {
            'name': 'user.view',
            'description': '查看用户',
            'resource': 'user',
            'action': 'view'
        },
        {
            'name': 'user.create',
            'description': '创建用户',
            'resource': 'user',
            'action': 'create'
        },
        {
            'name': 'user.update',
            'description': '更新用户',
            'resource': 'user',
            'action': 'update'
        },
        {
            'name': 'user.delete',
            'description': '删除用户',
            'resource': 'user',
            'action': 'delete'
        },
        
        # 角色管理权限
        {
            'name': 'role.view',
            'description': '查看角色',
            'resource': 'role',
            'action': 'view'
        },
        {
            'name': 'role.create',
            'description': '创建角色',
            'resource': 'role',
            'action': 'create'
        },
        {
            'name': 'role.update',
            'description': '更新角色',
            'resource': 'role',
            'action': 'update'
        },
        {
            'name': 'role.delete',
            'description': '删除角色',
            'resource': 'role',
            'action': 'delete'
        },
        
        # 权限管理权限
        {
            'name': 'permission.view',
            'description': '查看权限',
            'resource': 'permission',
            'action': 'view'
        },
        {
            'name': 'permission.assign',
            'description': '分配权限',
            'resource': 'permission',
            'action': 'assign'
        },
        
        # 系统管理权限
        {
            'name': 'system.config',
            'description': '系统配置',
            'resource': 'system',
            'action': 'config'
        },
        {
            'name': 'system.monitor',
            'description': '系统监控',
            'resource': 'system',
            'action': 'monitor'
        },
        
        # 日志管理权限
        {
            'name': 'log.view',
            'description': '查看日志',
            'resource': 'log',
            'action': 'view'
        },
        {
            'name': 'log.export',
            'description': '导出日志',
            'resource': 'log',
            'action': 'export'
        }
    ]
    
    created_count = 0
    for perm_data in permissions:
        try:
            # 检查权限是否已存在
            existing_perm = permission_service.get_permission_by_name(perm_data['name'])
            if not existing_perm:
                permission = permission_service.create_permission(perm_data)
                created_count += 1
                print(f"    ✓ 创建权限: {perm_data['name']}")
            else:
                print(f"    - 权限已存在: {perm_data['name']}")
        except Exception as e:
            print(f"    ❌ 创建权限失败 {perm_data['name']}: {e}")
    
    print(f"  权限初始化完成，创建了 {created_count} 个权限")


def init_roles():
    """初始化基础角色数据"""
    from app.services.role_service import role_service
    from app.services.permission_service import permission_service
    
    print("  创建基础角色...")
    
    # 定义基础角色
    roles = [
        {
            'name': 'super_admin',
            'description': '超级管理员，拥有所有权限',
            'is_system': True,
            'permissions': 'all'  # 特殊标记，表示拥有所有权限
        },
        {
            'name': 'admin',
            'description': '管理员，拥有大部分管理权限',
            'is_system': True,
            'permissions': [
                'user.view', 'user.create', 'user.update',
                'role.view', 'role.create', 'role.update',
                'permission.view', 'permission.assign',
                'log.view', 'log.export'
            ]
        },
        {
            'name': 'user_manager',
            'description': '用户管理员，负责用户管理',
            'is_system': True,
            'permissions': [
                'user.view', 'user.create', 'user.update',
                'log.view'
            ]
        },
        {
            'name': 'viewer',
            'description': '查看者，只能查看信息',
            'is_system': True,
            'permissions': [
                'user.view', 'role.view', 'permission.view', 'log.view'
            ]
        },
        {
            'name': 'user',
            'description': '普通用户，基础权限',
            'is_system': True,
            'permissions': []
        }
    ]
    
    created_count = 0
    for role_data in roles:
        try:
            # 检查角色是否已存在
            existing_role = role_service.get_role_by_name(role_data['name'])
            if not existing_role:
                # 创建角色
                permissions = role_data.pop('permissions')
                role = role_service.create_role(role_data)
                
                # 分配权限
                if permissions == 'all':
                    # 分配所有权限
                    all_permissions = permission_service.get_permissions_list()
                    permission_ids = [perm.id for perm in all_permissions['items']]
                    if permission_ids:
                        role_service.batch_assign_permissions_to_role(role.id, permission_ids)
                elif permissions:
                    # 分配指定权限
                    permission_ids = []
                    for perm_name in permissions:
                        permission = permission_service.get_permission_by_name(perm_name)
                        if permission:
                            permission_ids.append(permission.id)
                    
                    if permission_ids:
                        role_service.batch_assign_permissions_to_role(role.id, permission_ids)
                
                created_count += 1
                print(f"    ✓ 创建角色: {role_data['name']}")
            else:
                print(f"    - 角色已存在: {role_data['name']}")
        except Exception as e:
            print(f"    ❌ 创建角色失败 {role_data['name']}: {e}")
    
    print(f"  角色初始化完成，创建了 {created_count} 个角色")


def init_admin_user():
    """初始化管理员用户"""
    from app.services.user_service import user_service
    from app.services.role_service import role_service
    from app.services.log_service import log_service
    
    print("  创建默认管理员用户...")
    
    # 管理员用户信息
    admin_data = {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'Admin123456',
        'full_name': '系统管理员',
        'is_active': True,
        'is_verified': True,
        'is_superuser': True
    }
    
    try:
        # 检查管理员用户是否已存在
        existing_admin = user_service.get_user_by_username(admin_data['username'])
        if not existing_admin:
            # 创建管理员用户
            admin_user = user_service.create_user(admin_data)
            
            # 分配超级管理员角色
            super_admin_role = role_service.get_role_by_name('super_admin')
            if super_admin_role:
                user_service.assign_role_to_user(admin_user.id, super_admin_role.id)
            
            # 记录操作日志
            try:
                log_service.create_operation_log(
                    user_id=admin_user.id,
                    operation='create',
                    resource='user',
                    details={
                        'action': 'init_admin_user',
                        'username': admin_user.username,
                        'role': 'super_admin'
                    }
                )
            except Exception as log_error:
                print(f"    ⚠️  记录操作日志失败: {log_error}")
            
            print(f"    ✓ 创建管理员用户: {admin_data['username']}")
            print(f"    ✓ 默认密码: {admin_data['password']}")
            print("    ⚠️  请在首次登录后修改默认密码！")
        else:
            print(f"    - 管理员用户已存在: {admin_data['username']}")
    except Exception as e:
        print(f"    ❌ 创建管理员用户失败: {e}")
    
    print("  管理员用户初始化完成")


def create_migration_file():
    """创建数据库迁移文件"""
    print("📝 创建数据库迁移文件...")
    
    # 创建migrations目录
    migrations_dir = "migrations"
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
        print(f"  创建目录: {migrations_dir}")
    
    # 生成迁移文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_file = f"{migrations_dir}/{timestamp}_initial_migration.py"
    
    # 迁移文件内容
    migration_content = f'''"""
初始数据库迁移

创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
描述: 创建用户、角色、权限、日志等基础表结构
"""

from datetime import datetime, timezone
from app.models.base import create_tables, drop_tables


def upgrade():
    """执行迁移升级"""
    print("执行数据库迁移升级...")
    
    # 创建所有表
    create_tables()
    
    print("数据库迁移升级完成")


def downgrade():
    """执行迁移降级"""
    print("执行数据库迁移降级...")
    
    # 删除所有表
    drop_tables()
    
    print("数据库迁移降级完成")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "upgrade":
            upgrade()
        elif sys.argv[1] == "downgrade":
            downgrade()
        else:
            print("用法: python migration_file.py [upgrade|downgrade]")
    else:
        print("用法: python migration_file.py [upgrade|downgrade]")
'''
    
    # 写入迁移文件
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    
    print(f"  ✓ 创建迁移文件: {migration_file}")
    return migration_file


def main():
    """主函数"""
    print_header("数据库初始化")
    
    # 创建迁移文件
    migration_file = script_utils.create_migration_file("初始数据库迁移")
    
    # 初始化数据库
    success = init_database()
    
    if success:
        print_footer(True, "数据库初始化")
        print("📋 初始化内容:")
        print("  • 创建了所有数据库表")
        print("  • 初始化了基础权限数据")
        print("  • 创建了系统角色")
        print("  • 创建了默认管理员用户")
        
        print_admin_info()
        
        if migration_file:
            print(f"\n📄 迁移文件:")
            print(f"  {migration_file}")
        print("=" * 60)
    else:
        print_footer(False, "数据库初始化")
        sys.exit(1)


if __name__ == "__main__":
    main()