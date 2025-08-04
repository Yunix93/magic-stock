"""
应用主入口文件

用于启动现代化后台管理系统
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# 获取配置环境
config_name = os.getenv('FLASK_ENV', 'development')

# 创建应用实例
app, server = create_app(config_name)

if __name__ == '__main__':
    # 开发环境下直接运行
    debug = config_name == 'development'
    port = int(os.getenv('PORT', 8050))
    host = os.getenv('HOST', '127.0.0.1')
    
    print(f"🚀 启动现代化后台管理系统")
    print(f"📍 访问地址: http://{host}:{port}")
    print(f"🔧 运行环境: {config_name}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        dev_tools_hot_reload=debug,
        dev_tools_ui=debug
    )