# 权限控制系统使用指南

## 概述

本系统实现了一套完整的基于角色的访问控制（RBAC）权限管理系统，支持细粒度的权限控制和灵活的装饰器使用。

## 核心组件

### 1. 权限定义系统

#### PermissionDefinition
权限定义数据类，包含权限的基本信息：

```python
from app.core.permissions import PermissionDefinition

# 创建权限定义
permission = PermissionDefinition(
    name="user:create",      # 权限名称
    resource="user",         # 资源类型
    action="create",         # 操作类型
    description="创建用户",   # 权限描述
    group="用户管理"         # 权限分组
)
```

#### PermissionRegistry
权限注册表，管理所有系统权限：

```python
from app.core.permissions import permission_registry

# 注册自定义权限
custom_permission = PermissionDefinition(
    "custom:action", "custom", "action", "自定义操作"
)
permission_registry.register(custom_permission)

# 查询权限
perm = permission_registry.get("user:create")
all_perms = permission_registry.get_all()
user_perms = permission_registry.get_by_resource("user")
```

### 2. 角色权限管理

#### RolePermissionManager
管理角色和权限的映射关系：

```python
from app.core.permissions import role_permission_manager

# 为角色分配权限
role_permission_manager.assign_permission_to_role("editor", "user:update")

# 撤销角色权限
role_permission_manager.revoke_permission_from_role("editor", "user:delete")

# 检查角色权限
has_perm = role_permission_manager.has_permission(["editor"], "user:update")

# 获取用户所有权限
user_permissions = role_permission_manager.get_user_permissions(["admin", "editor"])
```

### 3. 权限检查器

#### PermissionChecker
统一的权限检查逻辑：

```python
from app.core.permissions import permission_checker

# 检查用户权限
has_permission = permission_checker.check_permission(user, "user:create")

# 检查用户角色
has_role = permission_checker.check_role(user, "admin")

# 获取用户所有权限
user_permissions = permission_checker.get_user_permissions(user)
```

## 装饰器使用

### 1. 基础认证装饰器

#### @login_required
要求用户必须登录：

```python
from app.core.auth import login_required

@login_required
def protected_view():
    return {"message": "只有登录用户才能访问"}
```

#### @permission_required
要求用户具有特定权限：

```python
from app.core.auth import permission_required

@permission_required("user:create")
def create_user():
    return {"message": "创建用户"}

@permission_required("user:read")
def get_user(user_id):
    return {"user_id": user_id}
```

#### @role_required
要求用户具有特定角色：

```python
from app.core.auth import role_required

@role_required("admin")
def admin_only_view():
    return {"message": "仅管理员可访问"}

@role_required(["admin", "manager"])  # 支持多个角色
def manager_view():
    return {"message": "管理员或经理可访问"}
```

#### @admin_required
要求管理员权限：

```python
from app.core.auth import admin_required

@admin_required
def admin_panel():
    return {"message": "管理员面板"}
```

### 2. 高级权限装饰器

#### @require_permissions
多权限验证，支持AND/OR逻辑：

```python
from app.core.permission_decorators import require_permissions

# 需要同时拥有多个权限（AND）
@require_permissions("user:read", "user:update", operator="AND")
def update_user_profile():
    return {"message": "更新用户资料"}

# 只需拥有其中一个权限（OR）
@require_permissions("user:read", "profile:read", operator="OR")
def view_profile():
    return {"message": "查看资料"}
```

#### @require_roles
多角色验证：

```python
from app.core.permission_decorators import require_roles

# 需要同时拥有多个角色
@require_roles("admin", "superuser", operator="AND")
def super_admin_action():
    return {"message": "超级管理员操作"}

# 只需拥有其中一个角色
@require_roles("admin", "manager", operator="OR")
def management_action():
    return {"message": "管理操作"}
```

#### @resource_owner_or_permission
资源所有者或权限验证：

```python
from app.core.permission_decorators import resource_owner_or_permission

@resource_owner_or_permission("user_id", "user:update")
def update_user(user_id):
    # 用户可以更新自己的信息，或者具有user:update权限的用户可以更新任何用户
    return {"message": f"更新用户 {user_id}"}
```

#### @conditional_permission
条件权限验证：

```python
from app.core.permission_decorators import conditional_permission

def needs_permission_for_post(user, request, *args, **kwargs):
    """只有POST请求才需要权限"""
    return request.method == 'POST'

@conditional_permission(needs_permission_for_post, "user:create")
def user_endpoint():
    if request.method == 'GET':
        return {"users": []}  # 查看不需要权限
    elif request.method == 'POST':
        return {"message": "创建用户"}  # 创建需要权限
```

#### @audit_log
自动审计日志记录：

```python
from app.core.permission_decorators import audit_log

@audit_log("create_user", "user")
def create_user():
    # 操作会自动记录到审计日志
    return {"message": "用户已创建"}

# 带资源ID的日志记录
def get_user_id(*args, **kwargs):
    return kwargs.get('user_id')

@audit_log("update_user", "user", get_resource_id=get_user_id)
def update_user(user_id):
    return {"message": f"用户 {user_id} 已更新"}
```

### 3. 便捷装饰器

系统提供了一些预定义的便捷装饰器：

```python
from app.core.permission_decorators import (
    user_management_required,
    role_management_required,
    system_admin_required,
    manager_or_admin_required
)

@user_management_required
def user_list():
    return {"users": []}

@role_management_required
def role_list():
    return {"roles": []}

@system_admin_required
def system_config():
    return {"config": {}}

@manager_or_admin_required
def management_dashboard():
    return {"dashboard": "data"}
```

## API响应格式

### 认证失败 (401)
```json
{
    "success": false,
    "error": "AuthenticationRequired",
    "message": "请先登录以访问此资源",
    "code": 401
}
```

### 权限不足 (403)
```json
{
    "success": false,
    "error": "PermissionDenied",
    "message": "您没有权限执行此操作: user:create",
    "code": 403
}
```

### 多权限验证失败
```json
{
    "success": false,
    "error": "PermissionDenied",
    "message": "缺少必需权限: user:create, user:update",
    "missing_permissions": ["user:create", "user:update"],
    "code": 403
}
```

## 实际使用示例

### 1. 用户管理API

```python
from flask import Blueprint, request, jsonify
from app.core.auth import login_required, permission_required
from app.core.permission_decorators import require_permissions, audit_log

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
@permission_required('user:list')
def list_users():
    """获取用户列表"""
    return jsonify({"users": []})

@user_bp.route('/users', methods=['POST'])
@require_permissions('user:create')
@audit_log('create_user', 'user')
def create_user():
    """创建用户"""
    data = request.get_json()
    # 创建用户逻辑
    return jsonify({"message": "用户创建成功"})

@user_bp.route('/users/<user_id>', methods=['PUT'])
@resource_owner_or_permission('user_id', 'user:update')
@audit_log('update_user', 'user', get_resource_id=lambda **kw: kw.get('user_id'))
def update_user(user_id):
    """更新用户"""
    data = request.get_json()
    # 更新用户逻辑
    return jsonify({"message": f"用户 {user_id} 更新成功"})

@user_bp.route('/users/<user_id>', methods=['DELETE'])
@require_permissions('user:delete')
@audit_log('delete_user', 'user', get_resource_id=lambda **kw: kw.get('user_id'))
def delete_user(user_id):
    """删除用户"""
    # 删除用户逻辑
    return jsonify({"message": f"用户 {user_id} 删除成功"})
```

### 2. 系统管理API

```python
from app.core.permission_decorators import system_admin_required

@user_bp.route('/admin/system/config', methods=['GET'])
@system_admin_required
def get_system_config():
    """获取系统配置"""
    return jsonify({"config": {}})

@user_bp.route('/admin/system/config', methods=['PUT'])
@system_admin_required
@audit_log('update_system_config', 'system')
def update_system_config():
    """更新系统配置"""
    data = request.get_json()
    # 更新配置逻辑
    return jsonify({"message": "系统配置更新成功"})
```

### 3. Dash页面权限控制

```python
import dash
from dash import html, dcc, callback, Input, Output
from app.core.auth import login_required, permission_required

# 页面级权限控制
@login_required
def user_management_layout():
    """用户管理页面布局"""
    return html.Div([
        html.H1("用户管理"),
        dcc.Graph(id="user-stats"),
        html.Div(id="user-list")
    ])

# 回调函数权限控制
@callback(
    Output("user-list", "children"),
    Input("refresh-button", "n_clicks")
)
@permission_required("user:list")
def update_user_list(n_clicks):
    """更新用户列表"""
    # 获取用户列表逻辑
    return html.Div("用户列表内容")
```

## 最佳实践

### 1. 权限命名规范
- 使用 `resource:action` 格式
- 资源名使用单数形式
- 操作名使用标准CRUD动词

```python
# 推荐
"user:create"
"role:update"
"system:config"

# 不推荐
"create_user"
"users:create"
"system_configuration"
```

### 2. 角色设计原则
- 遵循最小权限原则
- 角色层次化设计
- 避免权限重复

```python
# 角色层次示例
roles = {
    'guest': ['dashboard:view'],
    'user': ['dashboard:view', 'profile:read', 'profile:update'],
    'manager': ['user:read', 'user:list', 'role:read'] + user_permissions,
    'admin': ['*']  # 所有权限
}
```

### 3. 装饰器使用建议
- 优先使用具体的权限装饰器而不是角色装饰器
- 合理使用装饰器组合
- 为重要操作添加审计日志

```python
# 推荐：使用具体权限
@permission_required("user:delete")
def delete_user():
    pass

# 不推荐：使用角色（除非确实需要）
@role_required("admin")
def delete_user():
    pass
```

### 4. 错误处理
- 提供清晰的错误信息
- 区分认证和授权错误
- 记录安全相关的操作日志

```python
try:
    # 执行需要权限的操作
    result = protected_operation()
except AuthenticationError:
    # 处理认证错误
    return jsonify({"error": "请先登录"}), 401
except AuthorizationError:
    # 处理授权错误
    return jsonify({"error": "权限不足"}), 403
```

## 扩展和自定义

### 1. 添加自定义权限

```python
from app.core.permissions import permission_registry, PermissionDefinition

# 注册自定义权限
custom_permissions = [
    PermissionDefinition("report:generate", "report", "generate", "生成报告", "报告管理"),
    PermissionDefinition("export:data", "export", "data", "导出数据", "数据管理"),
]

for perm in custom_permissions:
    permission_registry.register(perm)
```

### 2. 创建自定义装饰器

```python
from functools import wraps
from app.core.auth import get_current_user
from app.core.permissions import has_permission

def report_access_required(f):
    """报告访问权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "认证失败"}), 401
        
        if not has_permission(user, "report:generate"):
            return jsonify({"error": "需要报告生成权限"}), 403
        
        return f(*args, **kwargs)
    return decorated_function
```

### 3. 动态权限检查

```python
def check_dynamic_permission(user, resource_type, resource_id, action):
    """动态权限检查"""
    # 基础权限检查
    base_permission = f"{resource_type}:{action}"
    if has_permission(user, base_permission):
        return True
    
    # 资源所有者检查
    if action in ['read', 'update'] and is_resource_owner(user, resource_type, resource_id):
        return True
    
    # 其他自定义逻辑
    return False
```

这个权限控制系统提供了灵活、安全、易用的权限管理功能，支持从简单的登录验证到复杂的多权限组合验证的各种场景。