#!/usr/bin/env python3
"""
数据库连接测试

验证数据库配置和连接是否正常
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_database_connection():
    """测试数据库连接"""
    print("🧪 开始测试数据库连接...")
    
    try:
        # 使用统一的配置管理
        from app.core.config_manager import config_manager
        
        # 测试不同数据库类型的连接
        test_results = {}
        
        # 1. 测试SQLite连接
        print("\n📊 测试SQLite数据库连接...")
        test_results['sqlite'] = test_sqlite_connection()
        
        # 2. 测试PostgreSQL连接（如果配置了）
        postgres_url = os.getenv('POSTGRES_TEST_URL')
        if postgres_url:
            print("\n🐘 测试PostgreSQL数据库连接...")
            test_results['postgresql'] = test_postgres_connection(postgres_url)
        
        # 3. 测试MySQL连接（如果配置了）
        mysql_url = os.getenv('MYSQL_TEST_URL')
        if mysql_url:
            print("\n🐬 测试MySQL数据库连接...")
            test_results['mysql'] = test_mysql_connection(mysql_url)
        
        # 输出测试结果
        print("\n📋 测试结果汇总:")
        for db_type, result in test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {db_type}: {status}")
        
        # 测试数据库管理器功能
        print("\n🔧 测试数据库管理器功能...")
        test_database_manager()
        
        return all(test_results.values())
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sqlite_connection():
    """测试SQLite连接"""
    try:
        from app.core.database import init_database
        from sqlalchemy import text
        
        # 使用内存数据库进行测试
        engine, session_factory = init_database('sqlite:///:memory:')
        session = session_factory()
        
        # 测试基本查询
        result = session.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1
        
        session.close()
        print("✅ SQLite连接测试通过")
        return True
        
    except Exception as e:
        print(f"❌ SQLite连接测试失败: {e}")
        return False

def test_postgres_connection(database_url):
    """测试PostgreSQL连接"""
    try:
        from app.core.database import init_database
        from sqlalchemy import text
        
        engine, session_factory = init_database(database_url)
        session = session_factory()
        
        # 测试基本查询
        result = session.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1
        
        # 测试PostgreSQL特有功能
        result = session.execute(text("SELECT version()")).fetchone()
        assert 'PostgreSQL' in result[0]
        
        session.close()
        print("✅ PostgreSQL连接测试通过")
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL连接测试失败: {e}")
        return False

def test_mysql_connection(database_url):
    """测试MySQL连接"""
    try:
        from app.core.database import init_database
        from sqlalchemy import text
        
        engine, session_factory = init_database(database_url)
        session = session_factory()
        
        # 测试基本查询
        result = session.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1
        
        # 测试MySQL特有功能
        result = session.execute(text("SELECT version()")).fetchone()
        print(f"MySQL版本: {result[0]}")
        
        session.close()
        print("✅ MySQL连接测试通过")
        return True
        
    except Exception as e:
        print(f"❌ MySQL连接测试失败: {e}")
        return False

def test_database_manager():
    """测试数据库管理器功能"""
    try:
        from app import create_app
        from app.core.database import DatabaseManager
        
        # 创建应用实例
        app, server = create_app('testing')
        
        with server.app_context():
            # 创建数据库管理器
            db_manager = DatabaseManager()
            
            # 测试连接检查
            assert db_manager.check_connection(), "数据库连接检查失败"
            print("✅ 数据库连接检查通过")
            
            # 测试获取数据库信息
            db_info = db_manager.get_database_info()
            assert 'dialect' in db_info, "数据库信息获取失败"
            print(f"✅ 数据库信息获取成功: {db_info['dialect']}")
            
            # 测试表操作
            tables = db_manager.get_all_tables()
            print(f"✅ 获取表列表成功: {len(tables)} 个表")
            
            print("✅ 数据库管理器功能测试通过")
            return True
            
    except Exception as e:
        print(f"❌ 数据库管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base_model():
    """测试基础模型功能"""
    try:
        from app.core.database import init_database, get_engine
        from app.models.base import BaseModel, Base
        from sqlalchemy import Column, String
        
        # 创建测试模型
        class TestModel(BaseModel):
            __tablename__ = 'test_model'
            name = Column(String(50), nullable=False)
        
        # 初始化数据库
        engine, session_factory = init_database('sqlite:///:memory:')
            
        # 创建表
        Base.metadata.create_all(bind=engine)
        
        # 测试模型创建
        test_instance = TestModel(name="测试数据")
        test_dict = test_instance.to_dict()
        
        assert 'id' in test_dict, "模型字典转换失败"
        assert test_dict['name'] == "测试数据", "模型数据不正确"
        print("✅ 基础模型功能测试通过")
        return True
            
    except Exception as e:
        print(f"❌ 基础模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始数据库系统测试...")
    
    tests = [
        ("数据库连接测试", test_database_connection),
        ("基础模型测试", test_base_model),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有数据库测试通过！")
        return True
    else:
        print("❌ 部分测试失败，请检查配置。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)