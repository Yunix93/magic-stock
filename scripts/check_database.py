#!/usr/bin/env python3
"""
数据库状态检查脚本

检查数据库连接状态和基础数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_database():
    """检查数据库状态"""
    print("🔍 检查数据库状态...")
    
    try:
        # 创建应用实例
        from app import create_app
        app, server = create_app()
        
        with server.app_context():
            # 初始化数据库连接
            from app.models.base import init_database
            database_url = server.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"  数据库URL: {database_url}")
            
            # 确保所有模型都被导入
            from app.models.user import User
            from app.models.role import Role
            from app.models.permission import Permission
            from app.models.logs import LoginLog, OperationLog
            from app.models.associations import UserRole, RolePermission
            
            # 初始化数据库连接
            engine, session = init_database(database_url)
            
            # 检查数据库连接
            print("📡 检查数据库连接...")
            try:
                # 执行简单查询测试连接
                from sqlalchemy import text
                result = session.execute(text("SELECT 1")).fetchone()
                print("✅ 数据库连接正常")
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                return False
            
            # 检查表结构
            print("📋 检查表结构...")
            tables_info = check_tables()
            
            # 检查基础数据
            print("📊 检查基础数据...")
            data_info = check_basic_data()
            
            # 输出统计信息
            print("\\n📈 数据库统计:")
            print(f"  表数量: {tables_info['table_count']}")
            print(f"  用户数量: {data_info['users']}")
            print(f"  角色数量: {data_info['roles']}")
            print(f"  权限数量: {data_info['permissions']}")
            print(f"  登录日志数量: {data_info['login_logs']}")
            print(f"  操作日志数量: {data_info['operation_logs']}")
            
            # 检查管理员账户
            print("\\n👤 检查管理员账户...")
            admin_info = check_admin_account()
            
            if admin_info['exists']:
                print("✅ 管理员账户存在")
                print(f"  用户名: {admin_info['username']}")
                print(f"  邮箱: {admin_info['email']}")
                print(f"  状态: {'激活' if admin_info['is_active'] else '未激活'}")
                print(f"  角色数量: {admin_info['role_count']}")
            else:
                print("❌ 管理员账户不存在")
            
            print("\\n🎉 数据库状态检查完成！")
            return True
            
    except Exception as e:
        print(f"❌ 数据库状态检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_tables():
    """检查表结构"""
    from sqlalchemy import inspect
    from app.models.base import engine
    
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    expected_tables = [
        'users', 'roles', 'permissions', 
        'user_roles', 'role_permissions',
        'login_logs', 'operation_logs'
    ]
    
    print(f"  发现 {len(table_names)} 个表")
    
    for table in expected_tables:
        if table in table_names:
            print(f"    ✓ {table}")
        else:
            print(f"    ❌ {table} (缺失)")
    
    return {
        'table_count': len(table_names),
        'tables': table_names
    }


def check_basic_data():
    """检查基础数据"""
    from app.services.user_service import user_service
    from app.services.role_service import role_service
    from app.services.permission_service import permission_service
    from app.services.log_service import log_service
    
    try:
        # 使用服务层获取统计数据
        user_stats = user_service.get_user_statistics()
        role_stats = role_service.get_role_statistics()
        permission_stats = permission_service.get_permission_statistics()
        
        # 获取日志统计
        login_logs_count = 0
        operation_logs_count = 0
        try:
            recent_login_logs = log_service.get_login_logs(limit=10000)
            login_logs_count = len(recent_login_logs.get('items', []))
            
            recent_operation_logs = log_service.get_operation_logs(limit=10000)
            operation_logs_count = len(recent_operation_logs.get('items', []))
        except Exception as log_error:
            print(f"  ⚠️  获取日志统计失败: {log_error}")
        
        return {
            'users': user_stats.get('total_users', 0),
            'roles': role_stats.get('total_roles', 0),
            'permissions': permission_stats.get('total_permissions', 0),
            'login_logs': login_logs_count,
            'operation_logs': operation_logs_count
        }
    except Exception as e:
        print(f"  ⚠️  获取数据统计失败: {e}")
        return {
            'users': 0,
            'roles': 0,
            'permissions': 0,
            'login_logs': 0,
            'operation_logs': 0
        }


def check_admin_account():
    """检查管理员账户"""
    from app.services.user_service import user_service
    
    try:
        admin_user = user_service.get_user_by_username('admin')
        
        if admin_user:
            # 获取用户角色
            try:
                user_roles = user_service.get_user_roles(admin_user.id)
                role_count = len(user_roles)
            except Exception as role_error:
                print(f"  ⚠️  获取用户角色失败: {role_error}")
                role_count = 0
            
            return {
                'exists': True,
                'username': admin_user.username,
                'email': admin_user.email,
                'is_active': admin_user.is_active,
                'role_count': role_count
            }
        else:
            return {'exists': False}
            
    except Exception as e:
        print(f"  ⚠️  检查管理员账户失败: {e}")
        return {'exists': False}


def main():
    """主函数"""
    print("=" * 60)
    print("现代化后台管理系统 - 数据库状态检查")
    print("=" * 60)
    
    success = check_database()
    
    if success:
        print("\\n" + "=" * 60)
        print("✅ 数据库状态检查完成！")
        print("=" * 60)
    else:
        print("\\n" + "=" * 60)
        print("❌ 数据库状态检查失败！")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()