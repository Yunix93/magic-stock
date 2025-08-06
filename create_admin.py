#!/usr/bin/env python3
"""
创建默认管理员用户的简化脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_admin_user():
    """创建默认管理员用户"""
    try:
        # 导入必要的模块
        from app.core.database import init_database, get_db_session
        from app.models.base import create_tables
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission
        from app.models.user_role import UserRole
        from app.models.role_permission import RolePermission
        
        print("🚀 开始创建管理员用户...")
        
        # 初始化数据库
        print("📋 初始化数据库连接...")
        engine, session_factory = init_database()
        
        # 创建所有表
        print("📋 创建数据库表...")
        create_tables()
        
        # 创建会话
        with get_db_session() as session:
            # 检查是否已存在admin用户
            existing_admin = session.query(User).filter(User.username == 'admin').first()
            if existing_admin:
                print("⚠️  管理员用户已存在")
                print(f"   用户名: {existing_admin.username}")
                print(f"   邮箱: {existing_admin.email}")
                print("   密码: Admin123456")
                return True
            
            # 创建管理员用户
            print("👤 创建管理员用户...")
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password='Admin123456',  # 这会自动哈希
                full_name='系统管理员',
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            
            session.add(admin_user)
            session.commit()
            
            print("✅ 管理员用户创建成功！")
            print("📝 登录信息:")
            print("   用户名: admin")
            print("   密码: Admin123456")
            print("   邮箱: admin@example.com")
            print("⚠️  请在首次登录后修改默认密码！")
            
            return True
            
    except Exception as e:
        print(f"❌ 创建管理员用户失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("现代化后台管理系统 - 创建管理员用户")
    print("=" * 60)
    
    success = create_admin_user()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 管理员用户创建完成！")
    else:
        print("❌ 管理员用户创建失败！")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()