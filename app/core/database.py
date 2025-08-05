"""
数据库管理工具

提供数据库操作的高级接口和统一的数据库初始化
"""

import os
import sys
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DatabaseError
from app.core.config_manager import config_manager
import logging

logger = logging.getLogger(__name__)

# 全局数据库连接
_engine = None
_session_factory = None


def init_database(database_url: str = None, **engine_options) -> Tuple[object, Session]:
    """
    初始化数据库连接
    
    Args:
        database_url: 数据库连接URL
        **engine_options: 引擎配置选项
        
    Returns:
        (engine, session): 数据库引擎和会话工厂
    """
    global _engine, _session_factory
    
    if database_url is None:
        # 从配置管理器获取数据库配置
        db_config = config_manager.get_database_config()
        database_url = db_config['SQLALCHEMY_DATABASE_URI']
        engine_options.update(db_config.get('SQLALCHEMY_ENGINE_OPTIONS', {}))
    
    try:
        # 创建数据库引擎
        _engine = create_engine(database_url, **engine_options)
        
        # 创建会话工厂
        _session_factory = sessionmaker(bind=_engine)
        
        # 测试连接
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info(f"数据库初始化成功: {database_url}")
        return _engine, _session_factory
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise DatabaseError(f"数据库初始化失败: {e}")


def get_engine():
    """获取数据库引擎"""
    global _engine
    if _engine is None:
        init_database()
    return _engine


def get_session() -> Session:
    """获取数据库会话"""
    global _session_factory
    if _session_factory is None:
        init_database()
    return _session_factory()


@contextmanager
def get_db_session(session=None):
    """
    数据库会话上下文管理器
    
    Args:
        session: 可选的外部会话，如果提供则使用外部会话，否则创建新会话
        
    Yields:
        Session: 数据库会话对象
    """
    if session is not None:
        # 使用外部提供的会话，不关闭
        yield session
    else:
        # 创建新会话，需要关闭
        new_session = get_session()
        try:
            yield new_session
        finally:
            new_session.close()


def create_tables():
    """创建所有数据表"""
    from app.models.base import Base
    
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = get_engine()
    
    @property
    def session(self):
        """获取数据库会话"""
        return get_session()
    
    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        session = self.session
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"事务回滚: {e}")
            raise DatabaseError(f"数据库事务失败: {e}")
        finally:
            session.close()
    
    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> Any:
        """执行原生SQL"""
        try:
            with self.transaction() as session:
                result = session.execute(text(sql), params or {})
                return result.fetchall()
        except SQLAlchemyError as e:
            logger.error(f"SQL执行失败: {e}")
            raise DatabaseError(f"SQL执行失败: {e}")
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except SQLAlchemyError as e:
            logger.error(f"检查表存在性失败: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表信息"""
        try:
            inspector = inspect(self.engine)
            if not self.table_exists(table_name):
                raise DatabaseError(f"表 {table_name} 不存在")
            
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            return {
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys
            }
        except SQLAlchemyError as e:
            logger.error(f"获取表信息失败: {e}")
            raise DatabaseError(f"获取表信息失败: {e}")
    
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except SQLAlchemyError as e:
            logger.error(f"获取表列表失败: {e}")
            raise DatabaseError(f"获取表列表失败: {e}")
    
    def backup_table(self, table_name: str, backup_name: str = None) -> str:
        """备份表"""
        if not backup_name:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{table_name}_backup_{timestamp}"
        
        try:
            sql = f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}"
            self.execute_sql(sql)
            logger.info(f"表 {table_name} 已备份为 {backup_name}")
            return backup_name
        except SQLAlchemyError as e:
            logger.error(f"备份表失败: {e}")
            raise DatabaseError(f"备份表失败: {e}")
    
    def drop_table(self, table_name: str, cascade: bool = False):
        """删除表"""
        try:
            cascade_clause = " CASCADE" if cascade else ""
            sql = f"DROP TABLE IF EXISTS {table_name}{cascade_clause}"
            self.execute_sql(sql)
            logger.info(f"表 {table_name} 已删除")
        except SQLAlchemyError as e:
            logger.error(f"删除表失败: {e}")
            raise DatabaseError(f"删除表失败: {e}")
    
    def truncate_table(self, table_name: str):
        """清空表数据"""
        try:
            # SQLite不支持TRUNCATE，使用DELETE
            if self.engine.dialect.name == 'sqlite':
                sql = f"DELETE FROM {table_name}"
            else:
                sql = f"TRUNCATE TABLE {table_name}"
            
            self.execute_sql(sql)
            logger.info(f"表 {table_name} 数据已清空")
        except SQLAlchemyError as e:
            logger.error(f"清空表失败: {e}")
            raise DatabaseError(f"清空表失败: {e}")
    
    def get_database_size(self) -> Dict[str, Any]:
        """获取数据库大小信息"""
        try:
            if self.engine.dialect.name == 'sqlite':
                # SQLite数据库大小
                db_path = self.engine.url.database
                if os.path.exists(db_path):
                    size = os.path.getsize(db_path)
                    return {'total_size': size, 'unit': 'bytes'}
                else:
                    return {'total_size': 0, 'unit': 'bytes'}
            
            elif self.engine.dialect.name == 'postgresql':
                # PostgreSQL数据库大小
                sql = """
                SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                       pg_database_size(current_database()) as size_bytes
                """
                result = self.execute_sql(sql)
                if result:
                    return {
                        'total_size': result[0][1],
                        'size_pretty': result[0][0],
                        'unit': 'bytes'
                    }
            
            elif self.engine.dialect.name == 'mysql':
                # MySQL数据库大小
                sql = """
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb,
                    SUM(data_length + index_length) AS size_bytes
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                """
                result = self.execute_sql(sql)
                if result:
                    return {
                        'total_size': result[0][1],
                        'size_mb': result[0][0],
                        'unit': 'bytes'
                    }
            
            return {'total_size': 0, 'unit': 'bytes'}
            
        except SQLAlchemyError as e:
            logger.error(f"获取数据库大小失败: {e}")
            raise DatabaseError(f"获取数据库大小失败: {e}")
    
    def optimize_database(self):
        """优化数据库"""
        try:
            if self.engine.dialect.name == 'sqlite':
                # SQLite优化
                self.execute_sql("VACUUM")
                self.execute_sql("ANALYZE")
                logger.info("SQLite数据库优化完成")
            
            elif self.engine.dialect.name == 'postgresql':
                # PostgreSQL优化
                self.execute_sql("VACUUM ANALYZE")
                logger.info("PostgreSQL数据库优化完成")
            
            elif self.engine.dialect.name == 'mysql':
                # MySQL优化
                tables = self.get_all_tables()
                for table in tables:
                    self.execute_sql(f"OPTIMIZE TABLE {table}")
                logger.info("MySQL数据库优化完成")
                
        except SQLAlchemyError as e:
            logger.error(f"数据库优化失败: {e}")
            raise DatabaseError(f"数据库优化失败: {e}")
    
    def check_connection(self) -> bool:
        """检查数据库连接"""
        try:
            self.execute_sql("SELECT 1")
            return True
        except Exception:
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        try:
            info = {
                'dialect': self.engine.dialect.name,
                'driver': self.engine.dialect.driver,
                'url': str(self.engine.url).replace(self.engine.url.password or '', '***'),
                'tables': self.get_all_tables(),
                'connection_status': self.check_connection()
            }
            
            # 添加数据库大小信息
            size_info = self.get_database_size()
            info.update(size_info)
            
            return info
            
        except Exception as e:
            logger.error(f"获取数据库信息失败: {e}")
            raise DatabaseError(f"获取数据库信息失败: {e}")


# 全局数据库管理器实例 - 延迟初始化
db_manager = None

def get_db_manager():
    """获取数据库管理器实例（延迟初始化）"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager