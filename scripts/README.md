# 数据库管理脚本

这个目录包含了用于管理现代化后台管理系统数据库的各种脚本。

## 脚本列表

### 1. init_database.py - 数据库初始化脚本

**功能：** 创建数据库表结构并初始化基础数据

**使用方法：**
```bash
python scripts/init_database.py
```

**执行内容：**
- 创建所有数据库表（用户、角色、权限、日志等）
- 初始化14个基础权限
- 创建5个系统角色（super_admin、admin、user_manager、viewer、user）
- 创建默认管理员用户（用户名：admin，密码：Admin123456）
- 生成初始数据库迁移文件

**注意事项：**
- 首次运行时会创建所有表和基础数据
- 重复运行时会跳过已存在的数据
- 请在首次登录后修改默认管理员密码

### 2. check_database.py - 数据库状态检查脚本

**功能：** 检查数据库连接状态和基础数据完整性

**使用方法：**
```bash
python scripts/check_database.py
```

**检查内容：**
- 数据库连接状态
- 表结构完整性
- 基础数据统计
- 管理员账户状态

**输出示例：**
```
📡 检查数据库连接...
✅ 数据库连接正常

📋 检查表结构...
  发现 7 个表
    ✓ users
    ✓ roles
    ✓ permissions
    ✓ user_roles
    ✓ role_permissions
    ✓ login_logs
    ✓ operation_logs

📈 数据库统计:
  表数量: 7
  用户数量: 1
  角色数量: 5
  权限数量: 14
  登录日志数量: 0
  操作日志数量: 1

👤 检查管理员账户...
✅ 管理员账户存在
  用户名: admin
  邮箱: admin@example.com
  状态: 激活
  角色数量: 1
```

### 3. migrate.py - 数据库迁移管理脚本

**功能：** 管理数据库迁移的创建、执行和回滚

**使用方法：**

创建新迁移：
```bash
python scripts/migrate.py create <migration_name>
```

列出所有迁移：
```bash
python scripts/migrate.py list
```

执行所有迁移升级：
```bash
python scripts/migrate.py upgrade
```

执行所有迁移降级：
```bash
python scripts/migrate.py downgrade
```

运行指定迁移：
```bash
python scripts/migrate.py run <migration_file> <upgrade|downgrade>
```

### 4. reset_database.py - 数据库重置脚本

**功能：** 删除所有数据并重新初始化数据库

**使用方法：**
```bash
python scripts/reset_database.py
```

**警告：** 
- 这个操作会删除所有现有数据！
- 执行前会要求确认（输入 'yes'）
- 适用于开发环境，生产环境请谨慎使用

**执行流程：**
1. 删除所有现有表
2. 重新创建表结构
3. 重新初始化基础数据
4. 重新创建默认管理员用户

## 初始化数据详情

### 默认权限列表

| 权限名称 | 描述 | 资源 | 操作 |
|---------|------|------|------|
| user.view | 查看用户 | user | view |
| user.create | 创建用户 | user | create |
| user.update | 更新用户 | user | update |
| user.delete | 删除用户 | user | delete |
| role.view | 查看角色 | role | view |
| role.create | 创建角色 | role | create |
| role.update | 更新角色 | role | update |
| role.delete | 删除角色 | role | delete |
| permission.view | 查看权限 | permission | view |
| permission.assign | 分配权限 | permission | assign |
| system.config | 系统配置 | system | config |
| system.monitor | 系统监控 | system | monitor |
| log.view | 查看日志 | log | view |
| log.export | 导出日志 | log | export |

### 默认角色列表

| 角色名称 | 描述 | 权限 |
|---------|------|------|
| super_admin | 超级管理员 | 所有权限 |
| admin | 管理员 | 大部分管理权限 |
| user_manager | 用户管理员 | 用户管理相关权限 |
| viewer | 查看者 | 只读权限 |
| user | 普通用户 | 基础权限 |

### 默认管理员账户

- **用户名：** admin
- **密码：** Admin123456
- **邮箱：** admin@example.com
- **角色：** super_admin
- **状态：** 激活

## 使用建议

### 开发环境

1. 首次设置：
   ```bash
   python scripts/init_database.py
   ```

2. 定期检查：
   ```bash
   python scripts/check_database.py
   ```

3. 重置开发数据：
   ```bash
   python scripts/reset_database.py
   ```

### 生产环境

1. 初始化：
   ```bash
   python scripts/init_database.py
   ```

2. 状态监控：
   ```bash
   python scripts/check_database.py
   ```

3. 迁移管理：
   ```bash
   python scripts/migrate.py upgrade
   ```

## 注意事项

1. **安全性：** 默认管理员密码必须在首次登录后修改
2. **备份：** 生产环境操作前请先备份数据库
3. **权限：** 确保脚本有足够的数据库操作权限
4. **环境：** 脚本会自动加载 `.env` 文件中的配置
5. **日志：** 所有操作都会记录详细的日志信息

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `.env` 文件中的数据库配置
   - 确认数据库服务是否运行
   - 检查数据库权限

2. **表已存在错误**
   - 使用 `reset_database.py` 重置数据库
   - 或手动删除现有表

3. **权限不足**
   - 确认数据库用户有创建表的权限
   - 检查文件系统权限

4. **模块导入错误**
   - 确认在项目根目录运行脚本
   - 检查 Python 路径配置

### 获取帮助

如果遇到问题，可以：
1. 查看脚本输出的详细错误信息
2. 检查日志文件
3. 运行 `check_database.py` 诊断问题
4. 查看项目文档