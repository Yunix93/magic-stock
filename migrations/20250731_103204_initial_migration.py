"""
初始数据库迁移

创建时间: 2025-07-31 10:32:04
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
