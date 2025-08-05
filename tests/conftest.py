"""
测试配置文件

提供测试所需的fixtures和配置
"""

import pytest
import tempfile
import os
from app import create_app
from app.models.base import init_database, create_tables, drop_tables, Base
from app.core.extensions import get_db_session


@pytest.fixture(scope="session")
def app():
    """创建测试应用实例"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp()
    
    # 创建测试应用
    app, server = create_app('testing')
    
    # 设置测试数据库
    server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    server.config['TESTING'] = True
    
    with server.app_context():
        # 初始化数据库
        init_database(server.config['SQLALCHEMY_DATABASE_URI'])
        create_tables()
        
        yield server
        
        # 清理
        drop_tables()
        
        # 安全地清理临时文件
        try:
            os.close(db_fd)
        except:
            pass
        
        try:
            os.unlink(db_path)
        except PermissionError:
            # Windows下可能出现权限问题，延迟删除
            import time
            time.sleep(0.1)
            try:
                os.unlink(db_path)
            except:
                pass  # 如果还是无法删除，就忽略


@pytest.fixture(scope="function")
def db_session(app):
    """提供数据库会话"""
    with app.app_context():
        session = get_db_session()
        
        # 开始事务
        transaction = session.begin()
        
        yield session
        
        # 回滚事务
        transaction.rollback()
        session.close()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建CLI运行器"""
    return app.test_cli_runner()


@pytest.fixture
def sample_user_data():
    """提供示例用户数据"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'full_name': 'Test User'
    }


@pytest.fixture
def create_test_user(db_session):
    """创建测试用户的工厂函数"""
    def _create_user(**kwargs):
        from app.models.user import User
        
        default_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123'
        }
        default_data.update(kwargs)
        
        user = User.create_user(**default_data)
        return user
    
    return _create_user


@pytest.fixture(params=[
    'postgresql://user:password@localhost/testdb',
    'mysql://user:password@localhost/testdb'
])
def database_url(request):
    """提供不同数据库URL用于测试"""
    return request.param