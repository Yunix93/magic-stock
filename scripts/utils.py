"""
脚本工具类

提供统一的应用初始化逻辑，消除脚本代码重复
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ScriptUtils:
    """脚本工具类，提供统一的应用初始化和数据库操作"""
    
    def __init__(self):
        self.app = None
        self.server = None
        self.engine = None
        self.session = None
    
    def init_app_context(self, environment='development'):
        """统一的应用初始化逻辑"""
        try:
            # 使用统一的配置管理
            from app.core.config_manager import config_manager
            
            # 创建应用实例
            from app import create_app
            self.app, self.server = create_app(environment)
            
            # 获取数据库配置
            db_config = config_manager.get_database_config()
            database_url = db_config['SQLALCHEMY_DATABASE_URI']
            
            print(f"环境: {environment}")
            print(f"数据库URL: {database_url}")
            
            return self.app, self.server
            
        except Exception as e:
            print(f"❌ 应用初始化失败: {e}")
            raise
    
    def init_database_connection(self):
        """初始化数据库连接"""
        try:
            with self.server.app_context():
                # 使用统一的数据库管理
                from app.core.database import init_database
                
                # 初始化数据库连接
                self.engine, session_factory = init_database()
                self.session = session_factory()
                
                # 确保所有模型都被导入
                from app.models import User, Role, Permission, LoginLog, OperationLog, UserRole, RolePermission
                
                print("✅ 数据库连接初始化完成")
                return self.engine, self.session
                
        except Exception as e:
            print(f"❌ 数据库连接初始化失败: {e}")
            raise
    
    def create_database_tables(self):
        """创建数据库表"""
        try:
            with self.server.app_context():
                from app.models.base import create_tables
                create_tables()
                print("✅ 数据库表创建完成")
                return True
                
        except Exception as e:
            print(f"❌ 数据库表创建失败: {e}")
            return False
    
    def drop_database_tables(self):
        """删除数据库表"""
        try:
            with self.server.app_context():
                from app.models.base import drop_tables
                drop_tables()
                print("✅ 数据库表删除完成")
                return True
                
        except Exception as e:
            print(f"❌ 数据库表删除失败: {e}")
            return False
    
    def test_database_connection(self):
        """测试数据库连接"""
        try:
            with self.server.app_context():
                from sqlalchemy import text
                result = self.session.execute(text("SELECT 1")).fetchone()
                print("✅ 数据库连接测试成功")
                return True
                
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {e}")
            return False
    
    def get_database_statistics(self):
        """获取数据库统计信息"""
        try:
            with self.server.app_context():
                from app.models import User, Role, Permission, LoginLog, OperationLog
                
                stats = {
                    'users': len(User.get_all()),
                    'roles': len(Role.get_all()),
                    'permissions': len(Permission.get_all()),
                    'login_logs': len(LoginLog.get_recent_logs(hours=24*365, limit=10000)),
                    'operation_logs': len(OperationLog.get_recent_logs(hours=24*365, limit=10000))
                }
                
                return stats
                
        except Exception as e:
            print(f"❌ 获取数据库统计失败: {e}")
            return {
                'users': 0,
                'roles': 0,
                'permissions': 0,
                'login_logs': 0,
                'operation_logs': 0
            }
    
    def check_table_structure(self):
        """检查表结构"""
        try:
            with self.server.app_context():
                from sqlalchemy import inspect
                
                inspector = inspect(self.engine)
                table_names = inspector.get_table_names()
                
                expected_tables = [
                    'users', 'roles', 'permissions', 
                    'user_roles', 'role_permissions',
                    'login_logs', 'operation_logs'
                ]
                
                print(f"发现 {len(table_names)} 个表:")
                
                table_status = {}
                for table in expected_tables:
                    if table in table_names:
                        print(f"  ✓ {table}")
                        table_status[table] = True
                    else:
                        print(f"  ❌ {table} (缺失)")
                        table_status[table] = False
                
                return {
                    'table_count': len(table_names),
                    'tables': table_names,
                    'expected_tables': expected_tables,
                    'table_status': table_status
                }
                
        except Exception as e:
            print(f"❌ 检查表结构失败: {e}")
            return None
    
    def check_admin_account(self):
        """检查管理员账户"""
        try:
            with self.server.app_context():
                from app.models.user import User
                
                admin_user = User.get_by_username('admin')
                
                if admin_user:
                    roles = admin_user.get_roles()
                    return {
                        'exists': True,
                        'username': admin_user.username,
                        'email': admin_user.email,
                        'is_active': admin_user.is_active,
                        'is_verified': admin_user.is_verified,
                        'role_count': len(roles),
                        'roles': [role.name for role in roles]
                    }
                else:
                    return {'exists': False}
                    
        except Exception as e:
            print(f"❌ 检查管理员账户失败: {e}")
            return {'exists': False}
    
    def create_migration_file(self, description="数据库迁移"):
        """创建数据库迁移文件"""
        try:
            # 创建migrations目录
            migrations_dir = "migrations"
            if not os.path.exists(migrations_dir):
                os.makedirs(migrations_dir)
                print(f"创建目录: {migrations_dir}")
            
            # 生成迁移文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            migration_file = f"{migrations_dir}/{timestamp}_{description.replace(' ', '_').lower()}.py"
            
            # 迁移文件内容
            migration_content = f'''"""
{description}

创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
描述: {description}
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
            
            print(f"✓ 创建迁移文件: {migration_file}")
            return migration_file
            
        except Exception as e:
            print(f"❌ 创建迁移文件失败: {e}")
            return None
    
    def print_header(self, title):
        """打印脚本标题"""
        print("=" * 60)
        print(f"现代化后台管理系统 - {title}")
        print("=" * 60)
    
    def print_footer(self, success, title):
        """打印脚本结果"""
        print("\n" + "=" * 60)
        if success:
            print(f"✅ {title}完成！")
        else:
            print(f"❌ {title}失败！")
        print("=" * 60)
    
    def print_admin_info(self):
        """打印管理员信息"""
        print("\n📝 默认管理员账户:")
        print("  用户名: admin")
        print("  密码: Admin123456")
        print("  ⚠️  请在首次登录后修改默认密码！")
    
    def confirm_operation(self, message):
        """确认操作"""
        confirm = input(f"{message} (输入 'yes' 确认): ")
        return confirm.lower() == 'yes'
    
    def cleanup(self):
        """清理资源"""
        if self.session:
            self.session.close()
        print("✅ 资源清理完成")


# 全局工具实例
script_utils = ScriptUtils()


def get_script_utils():
    """获取脚本工具实例"""
    return script_utils


# 便捷函数
def init_app_context(environment='development'):
    """初始化应用上下文的便捷函数"""
    return script_utils.init_app_context(environment)


def init_database_connection():
    """初始化数据库连接的便捷函数"""
    return script_utils.init_database_connection()


def create_database_tables():
    """创建数据库表的便捷函数"""
    return script_utils.create_database_tables()


def drop_database_tables():
    """删除数据库表的便捷函数"""
    return script_utils.drop_database_tables()


def test_database_connection():
    """测试数据库连接的便捷函数"""
    return script_utils.test_database_connection()


def get_database_statistics():
    """获取数据库统计的便捷函数"""
    return script_utils.get_database_statistics()


def check_table_structure():
    """检查表结构的便捷函数"""
    return script_utils.check_table_structure()


def check_admin_account():
    """检查管理员账户的便捷函数"""
    return script_utils.check_admin_account()


def print_header(title):
    """打印标题的便捷函数"""
    script_utils.print_header(title)


def print_footer(success, title):
    """打印结果的便捷函数"""
    script_utils.print_footer(success, title)


def print_admin_info():
    """打印管理员信息的便捷函数"""
    script_utils.print_admin_info()


def confirm_operation(message):
    """确认操作的便捷函数"""
    return script_utils.confirm_operation(message)