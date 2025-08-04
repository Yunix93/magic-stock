# 项目结构说明

## 目录结构

```
modern_admin_system/
├── app/                        # 主应用目录
│   ├── __init__.py            # 应用工厂函数
│   ├── main.py                # 应用入口文件
│   ├── config/                # 配置管理
│   │   └── __init__.py
│   ├── core/                  # 核心功能
│   │   └── __init__.py
│   ├── models/                # 数据模型
│   │   └── __init__.py
│   ├── services/              # 业务服务层
│   │   └── __init__.py
│   ├── api/                   # API接口
│   │   └── __init__.py
│   ├── views/                 # 页面视图
│   │   ├── auth/              # 认证页面
│   │   ├── dashboard/         # 仪表板
│   │   ├── users/             # 用户管理
│   │   ├── system/            # 系统管理
│   │   ├── components/        # 公共组件
│   │   └── __init__.py
│   ├── callbacks/             # Dash回调函数
│   │   └── __init__.py
│   └── static/                # 静态资源
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/                # 数据库迁移
├── tests/                     # 测试文件
├── docker/                    # Docker配置
├── scripts/                   # 部署脚本
│   └── init_db.py            # 数据库初始化脚本
├── requirements/              # 依赖文件
│   ├── base.txt              # 基础依赖
│   ├── development.txt       # 开发环境依赖
│   ├── production.txt        # 生产环境依赖
│   └── testing.txt           # 测试环境依赖
├── assets/                    # 静态资源（保留原有）
├── backup_old_system/         # 旧系统备份
├── .gitignore                # Git忽略文件
├── requirements.txt          # 主依赖文件
└── README.md                 # 项目说明
```

## 模块说明

### app/ - 主应用目录
- **__init__.py**: 应用工厂函数，负责创建和配置应用实例
- **main.py**: 应用入口文件，用于启动服务器

### app/config/ - 配置管理
- 分环境配置管理（开发、测试、生产）
- 环境变量加载和验证
- 敏感信息安全处理

### app/core/ - 核心功能
- 认证装饰器和权限控制
- 自定义异常类
- 工具函数和通用组件

### app/models/ - 数据模型
- SQLAlchemy ORM模型定义
- 数据库关系和约束
- 模型基类和通用方法

### app/services/ - 业务服务层
- 业务逻辑封装
- 数据处理和验证
- 外部服务集成

### app/api/ - API接口
- RESTful API端点
- 请求验证和响应格式化
- API文档和版本管理

### app/views/ - 页面视图
- Dash页面布局和组件
- 响应式设计实现
- 用户界面交互

### app/callbacks/ - 回调函数
- Dash交互回调
- 事件处理逻辑
- 状态管理

## 开发指南

### 环境设置
```bash
# 安装开发环境依赖
pip install -r requirements/development.txt

# 初始化数据库
python scripts/init_database.py

# 启动开发服务器
python app/main.py
```

### 代码规范
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 使用 MyPy 进行类型检查
- 编写单元测试和文档

### 部署流程
- 开发环境：直接运行 `python app/main.py`
- 生产环境：使用 Docker 容器化部署
- 测试环境：使用 pytest 运行测试套件

## 下一步开发任务

1. ✅ **任务 1.1**: 创建项目目录结构和基础文件
2. ✅ **任务 1.2**: 配置环境管理系统
3. ✅ **任务 1.3**: 设置数据库连接和ORM配置

项目基础架构已经搭建完成，可以开始后续的开发任务。