#!/usr/bin/env python3
"""
数据库迁移管理脚本

管理数据库迁移的创建、执行和回滚
"""

import os
import sys
import glob
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_migration(name: str):
    """创建新的迁移文件"""
    print(f"📝 创建迁移文件: {name}")
    
    # 创建migrations目录
    migrations_dir = "migrations"
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
    
    # 生成迁移文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_file = f"{migrations_dir}/{timestamp}_{name}.py"
    
    # 迁移文件模板
    migration_template = f'''"""
数据库迁移: {name}

创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
描述: {name}
"""

from datetime import datetime, timezone


def upgrade():
    """执行迁移升级"""
    print("执行迁移升级: {name}")
    
    # 在这里添加升级逻辑
    # 例如: 创建表、添加列、修改数据等
    
    print("迁移升级完成: {name}")


def downgrade():
    """执行迁移降级"""
    print("执行迁移降级: {name}")
    
    # 在这里添加降级逻辑
    # 例如: 删除表、删除列、回滚数据等
    
    print("迁移降级完成: {name}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "upgrade":
            upgrade()
        elif sys.argv[1] == "downgrade":
            downgrade()
        else:
            print("用法: python {{migration_file}} [upgrade|downgrade]")
    else:
        print("用法: python {{migration_file}} [upgrade|downgrade]")
'''
    
    # 写入迁移文件
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_template)
    
    print(f"✅ 迁移文件已创建: {migration_file}")
    return migration_file


def list_migrations():
    """列出所有迁移文件"""
    print("📋 迁移文件列表:")
    
    migrations_dir = "migrations"
    if not os.path.exists(migrations_dir):
        print("  没有找到迁移文件")
        return []
    
    # 获取所有迁移文件
    migration_files = glob.glob(f"{migrations_dir}/*.py")
    migration_files.sort()
    
    if not migration_files:
        print("  没有找到迁移文件")
        return []
    
    for i, migration_file in enumerate(migration_files, 1):
        filename = os.path.basename(migration_file)
        print(f"  {i}. {filename}")
    
    return migration_files


def run_migration(migration_file: str, action: str):
    """运行指定的迁移文件"""
    if not os.path.exists(migration_file):
        print(f"❌ 迁移文件不存在: {migration_file}")
        return False
    
    try:
        # 动态导入迁移模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration", migration_file)
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)
        
        # 执行迁移
        if action == "upgrade":
            migration_module.upgrade()
        elif action == "downgrade":
            migration_module.downgrade()
        else:
            print(f"❌ 无效的操作: {action}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_migrations(action: str):
    """运行所有迁移文件"""
    migration_files = list_migrations()
    
    if not migration_files:
        print("没有找到迁移文件")
        return True
    
    print(f"\n🚀 开始执行所有迁移 ({action})...")
    
    success_count = 0
    for migration_file in migration_files:
        filename = os.path.basename(migration_file)
        print(f"\n执行迁移: {filename}")
        
        if run_migration(migration_file, action):
            success_count += 1
            print(f"✅ 迁移成功: {filename}")
        else:
            print(f"❌ 迁移失败: {filename}")
            break
    
    print(f"\n📊 迁移结果: {success_count}/{len(migration_files)} 成功")
    return success_count == len(migration_files)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("数据库迁移管理工具")
        print("\n用法:")
        print("  python migrate.py create <migration_name>  # 创建新迁移")
        print("  python migrate.py list                     # 列出所有迁移")
        print("  python migrate.py upgrade                  # 执行所有迁移升级")
        print("  python migrate.py downgrade                # 执行所有迁移降级")
        print("  python migrate.py run <file> <action>      # 运行指定迁移")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 3:
            print("❌ 请提供迁移名称")
            print("用法: python migrate.py create <migration_name>")
            return
        
        migration_name = sys.argv[2]
        create_migration(migration_name)
    
    elif command == "list":
        list_migrations()
    
    elif command == "upgrade":
        # 创建应用实例
        from app import create_app
        app, server = create_app()
        
        with server.app_context():
            # 初始化数据库连接
            from app.models.base import init_database
            database_url = server.config.get('SQLALCHEMY_DATABASE_URI')
            init_database(database_url)
            
            # 确保所有模型都被导入
            from app.models.user import User
            from app.models.role import Role, Permission
            from app.models.logs import LoginLog, OperationLog
            
            run_all_migrations("upgrade")
    
    elif command == "downgrade":
        # 创建应用实例
        from app import create_app
        app, server = create_app()
        
        with server.app_context():
            # 初始化数据库连接
            from app.models.base import init_database
            database_url = server.config.get('SQLALCHEMY_DATABASE_URI')
            init_database(database_url)
            
            # 确保所有模型都被导入
            from app.models.user import User
            from app.models.role import Role, Permission
            from app.models.logs import LoginLog, OperationLog
            
            run_all_migrations("downgrade")
    
    elif command == "run":
        if len(sys.argv) < 4:
            print("❌ 参数不足")
            print("使用: python migrate.py run <migration_file> <upgrade|downgrade>")
            return
        
        migration_file = sys.argv[2]
        action = sys.argv[3]
        
        # 创建应用实例
        from app import create_app
        app, server = create_app()
        
        with server.app_context():
            # 初始化数据库连接
            from app.models.base import init_database
            database_url = server.config.get('SQLALCHEMY_DATABASE_URI')
            init_database(database_url)
            
            run_migration(migration_file, action)
    
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python migrate.py' 查看帮助")


if __name__ == "__main__":
    main()