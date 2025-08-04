#!/usr/bin/env python3
"""
数据库重置脚本

删除所有数据并重新初始化数据库
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def reset_database():
    """重置数据库"""
    print("⚠️  数据库重置操作")
    print("这将删除所有现有数据并重新初始化数据库！")
    
    # 确认操作
    confirm = input("确定要继续吗？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return False
    
    try:
        # 加载环境变量
        from app.core.extensions import load_environment_variables
        load_environment_variables()
        
        # 创建应用实例
        from app import create_app
        app, server = create_app()
        
        with server.app_context():
            # 初始化数据库连接
            from app.models.base import init_database, drop_tables, create_tables
            database_url = server.config.get('SQLALCHEMY_DATABASE_URI')
            print(f"数据库URL: {database_url}")
            
            # 确保所有模型都被导入
            from app.models.user import User
            from app.models.role import Role, Permission
            from app.models.logs import LoginLog, OperationLog
            
            # 初始化数据库连接
            engine, session = init_database(database_url)
            
            # 删除所有表
            print("🗑️  删除现有数据库表...")
            drop_tables()
            print("✅ 数据库表删除完成")
            
            # 重新创建所有表
            print("📋 重新创建数据库表...")
            create_tables()
            print("✅ 数据库表创建完成")
            
            # 重新初始化基础数据
            print("📊 重新初始化基础数据...")
            from scripts.init_database import init_basic_data
            init_basic_data()
            print("✅ 基础数据初始化完成")
            
            print("🎉 数据库重置成功！")
            print("\n📝 默认管理员账户:")
            print("  用户名: admin")
            print("  密码: Admin123456")
            print("  ⚠️  请在首次登录后修改默认密码！")
            
            return True
            
    except Exception as e:
        print(f"❌ 数据库重置失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("现代化后台管理系统 - 数据库重置")
    print("=" * 60)
    
    success = reset_database()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 数据库重置完成！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 数据库重置失败！")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()