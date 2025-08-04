# 数据库配置指南

## 概述

现代化后台管理系统支持多种数据库类型，包括SQLite、PostgreSQL和MySQL。本文档详细说明了如何配置和使用这些数据库。

## 支持的数据库

### 1. SQLite（默认）
- **优点**: 无需安装，适合开发和小型应用
- **缺点**: 不支持并发写入，功能有限
- **推荐用途**: 开发环境、测试环境、小型应用

### 2. PostgreSQL（推荐生产环境）
- **优点**: 功能强大，支持高并发，ACID兼容
- **缺点**: 需要单独安装和配置
- **推荐用途**: 生产环境、大型应用

### 3. MySQL
- **优点**: 广泛使用，性能良好
- **缺点**: 某些高级功能支持有限
- **推荐用途**: 传统Web应用、中等规模应用

## 配置方法

### 环境变量配置

在 `.env` 文件中设置数据库连接URL：

```bash
# SQLite（默认）
DATABASE_URL=sqlite:///admin_system.db

# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/admin_system

# MySQL
DATABASE_URL=mysql://username:password@localhost:3306/admin_system
```

### 不同环境的配置

#### 开发环境
```bash
# .env
DATABASE_URL=sqlite:///dev_admin_system.db
DEV_DATABASE_URL=sqlite:///dev_admin_system.db
```

#### 测试环境
```bash
# 测试环境使用内存数据库
DATABASE_URL=sqlite:///:memory:
```

#### 生产环境
```bash
# 生产环境必须使用PostgreSQL或MySQL
DATABASE_URL=postgresql://user:pass@prod-db:5432/admin_system
REDIS_URL=redis://prod-redis:6379/0
```

## 数据库初始化

### 1. 基础初始化

```bash
# 初始化数据库连接和表结构
python scripts/init_db.py --init
```

### 2. 创建迁移

```bash
# 创建初始迁移文件
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 3. 完整设置

```bash
# 执行完整的数据库设置（推荐）
python scripts/init_db.py --all
```

## 数据库迁移

### Alembic迁移工具

系统使用Alembic进行数据库版本管理：

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述变更内容"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### 迁移最佳实践

1. **总是先备份生产数据库**
2. **在测试环境验证迁移**
3. **使用描述性的迁移消息**
4. **避免在迁移中删除数据**
5. **大型变更分步进行**

## 数据库管理

### 使用DatabaseManager

```python
from app.core.database import DatabaseManager

# 创建管理器实例
db_manager = DatabaseManager()

# 检查连接
if db_manager.check_connection():
    print("数据库连接正常")

# 获取数据库信息
info = db_manager.get_database_info()
print(f"数据库类型: {info['dialect']}")

# 备份表
db_manager.backup_table('users', 'users_backup_20240101')

# 优化数据库
db_manager.optimize_database()
```

### 事务管理

```python
# 使用事务上下文管理器
with db_manager.transaction() as session:
    # 执行数据库操作
    user = User(name="张三")
    session.add(user)
    # 自动提交或回滚
```

## 性能优化

### 连接池配置

不同数据库的连接池配置：

```python
# PostgreSQL
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}

# MySQL
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'connect_args': {'charset': 'utf8mb4'}
}

# SQLite
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': False,
    'pool_recycle': -1,
    'connect_args': {'check_same_thread': False}
}
```

### 索引优化

```python
# 在模型中定义索引
class User(BaseModel):
    __tablename__ = 'users'
    
    email = Column(String(255), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, index=True)
```

## 备份和恢复

### 自动备份

```python
# 备份单个表
db_manager.backup_table('users')

# 备份整个数据库（PostgreSQL）
import subprocess
subprocess.run([
    'pg_dump', '-h', 'localhost', '-U', 'username', 
    '-d', 'database_name', '-f', 'backup.sql'
])
```

### 数据恢复

```python
# 从备份恢复（PostgreSQL）
subprocess.run([
    'psql', '-h', 'localhost', '-U', 'username',
    '-d', 'database_name', '-f', 'backup.sql'
])
```

## 故障排除

### 常见问题

1. **连接超时**
   - 检查数据库服务是否运行
   - 验证连接参数
   - 检查防火墙设置

2. **权限错误**
   - 确认数据库用户权限
   - 检查数据库和表的访问权限

3. **编码问题**
   - 确保数据库使用UTF-8编码
   - MySQL需要设置charset=utf8mb4

4. **迁移失败**
   - 检查迁移文件语法
   - 验证数据库结构
   - 查看详细错误日志

### 调试工具

```bash
# 测试数据库连接
python test_database.py

# 查看数据库信息
python -c "
from app.core.database import db_manager
print(db_manager.get_database_info())
"

# 检查表结构
python -c "
from app.core.database import db_manager
print(db_manager.get_table_info('users'))
"
```

## 安全建议

1. **使用强密码**
2. **限制数据库访问IP**
3. **定期更新数据库软件**
4. **启用SSL连接**
5. **定期备份数据**
6. **监控异常访问**

## 监控和维护

### 性能监控

```python
# 获取数据库大小
size_info = db_manager.get_database_size()
print(f"数据库大小: {size_info}")

# 优化数据库
db_manager.optimize_database()
```

### 定期维护任务

1. **每日**: 检查连接状态
2. **每周**: 优化数据库
3. **每月**: 备份数据
4. **每季度**: 清理日志表