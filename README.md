# Dash Web Application

一个基于 Dash 和 Flask 构建的现代化 Web 应用程序，具有用户认证、权限管理和响应式界面。

## 功能特性

- 🔐 **用户认证系统** - 基于 Flask-Login 的完整登录/登出功能
- 👥 **角色权限管理** - 使用 Flask-Principal 实现基于角色的访问控制
- 🎨 **现代化界面** - 基于 Feffery Antd Components 的美观 UI
- 📱 **响应式设计** - 支持多种设备和屏幕尺寸
- 🔒 **安全防护** - 浏览器版本检查、重复登录检测
- 💧 **水印功能** - 可选的全屏水印保护
- ⚡ **高性能** - 内置压缩和优化功能

## 项目结构

```
├── app.py              # 主应用程序入口
├── server.py           # Flask 服务器配置
├── requirements.txt    # 项目依赖
├── assets/            # 静态资源文件
├── callbacks/         # Dash 回调函数
├── components/        # 可复用组件
├── configs/           # 配置文件
├── models/            # 数据模型
├── utils/             # 工具函数
└── views/             # 页面视图
```

## 快速开始

### 环境要求

- Python 3.8 - 3.13
- 推荐使用虚拟环境

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   ```

3. **激活虚拟环境**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **运行应用**
   ```bash
   python app.py
   ```

6. **访问应用**
   
   打开浏览器访问 `http://localhost:8050`

## 开发模式

应用支持开发模式，具有以下特性：
- 热重载
- 调试信息
- 详细错误提示

```bash
python app.py  # 开发模式运行
```

## 生产部署

推荐使用 Gunicorn 进行生产部署：

```bash
pip install gunicorn
gunicorn server:server -b 0.0.0.0:8000
```

## 主要依赖

- **Dash** - Web 应用框架
- **Feffery Antd Components** - UI 组件库
- **Flask-Login** - 用户认证
- **Flask-Principal** - 权限管理
- **Peewee** - 数据库 ORM
- **Pandas** - 数据处理

## 配置说明

应用配置位于 `configs/` 目录下，包括：
- 基础配置 (BaseConfig)
- 路由配置 (RouterConfig)  
- 认证配置 (AuthConfig)

## 浏览器支持

应用内置浏览器版本检查，确保最佳用户体验：
- 不支持 IE 浏览器
- 支持现代浏览器的最新版本

## 开发指南

### 添加新页面

1. 在 `views/` 目录下创建页面文件
2. 在 `configs/RouterConfig` 中注册路由
3. 配置相应的权限规则

### 添加新组件

1. 在 `components/` 目录下创建组件文件
2. 实现组件的渲染逻辑
3. 在需要的页面中导入使用

### 数据库操作

使用 Peewee ORM 进行数据库操作，模型定义在 `models/` 目录下。

## 许可证

[添加你的许可证信息]

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

[添加你的联系方式]