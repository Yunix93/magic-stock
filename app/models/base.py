"""
数据库基础模型

提供所有数据模型的基础类和通用功能
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, String, DateTime, Boolean, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import event
from app.core.constants import DatabaseTables
from app.core.utils import generate_uuid
import logging

logger = logging.getLogger(__name__)

# 创建基础模型类
Base = declarative_base()

# 导入统一的数据库管理
# 注意：这里使用延迟导入避免循环依赖


class BaseModel(Base):
    """数据库基础模型类"""
    
    __abstract__ = True
    
    # 主键ID，使用UUID
    id = Column(
        String(36), 
        primary_key=True, 
        default=generate_uuid,
        comment="主键ID"
    )
    
    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="创建时间"
    )
    
    # 更新时间
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="更新时间"
    )
    
    # 软删除标记
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已删除"
    )
    
    # 删除时间
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )
    
    @declared_attr
    def __tablename__(cls):
        """自动生成表名"""
        # 将类名转换为下划线格式
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def __init__(self, **kwargs):
        """初始化模型实例"""
        # 确保ID被设置
        if 'id' not in kwargs:
            kwargs['id'] = generate_uuid()
        
        # 确保时间戳被设置
        now = datetime.now(timezone.utc)
        if 'created_at' not in kwargs:
            kwargs['created_at'] = now
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = now
        
        super().__init__(**kwargs)
    
    def to_dict(self, exclude_fields: List[str] = None) -> Dict[str, Any]:
        """转换为字典格式"""
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # 处理日期时间格式
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude_fields: List[str] = None):
        """从字典更新模型属性"""
        exclude_fields = exclude_fields or ['id', 'created_at', 'updated_at']
        
        for key, value in data.items():
            if key not in exclude_fields and hasattr(self, key):
                setattr(self, key, value)
    
    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self):
        """恢复软删除"""
        self.is_deleted = False
        self.deleted_at = None
    
    @classmethod
    def create(cls, **kwargs):
        """创建新实例"""
        from app.core.database import get_session
        session = get_session()
        try:
            instance = cls(**kwargs)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        finally:
            session.close()
    
    @classmethod
    def get_by_id(cls, id: str):
        """根据ID获取实例"""
        from app.core.database import get_session
        session = get_session()
        try:
            return session.query(cls).filter(
                cls.id == id,
                cls.is_deleted == False
            ).first()
        finally:
            session.close()
    
    @classmethod
    def get_all(cls, include_deleted: bool = False):
        """获取所有实例"""
        from app.core.database import get_session
        session = get_session()
        try:
            query = session.query(cls)
            if not include_deleted:
                query = query.filter(cls.is_deleted == False)
            return query.all()
        finally:
            session.close()
    
    @classmethod
    def filter_by(cls, include_deleted: bool = False, **kwargs):
        """根据条件筛选"""
        try:
            from app.core.database import get_session
            session = get_session()
            query = session.query(cls).filter_by(**kwargs)
            if not include_deleted:
                query = query.filter(cls.is_deleted == False)
            return query
        except Exception:
            # 返回一个空的查询对象模拟
            class EmptyQuery:
                def first(self):
                    return None
                def all(self):
                    return []
                def count(self):
                    return 0
            return EmptyQuery()
    
    def save(self):
        """保存实例"""
        from app.core.database import get_session
        session = get_session()
        try:
            # 检查对象是否已经在会话中
            if self in session:
                session.commit()
                session.refresh(self)
            else:
                # 如果对象已经在其他会话中，先合并
                merged_obj = session.merge(self)
                session.commit()
                session.refresh(merged_obj)
                # 更新当前对象的属性
                for key, value in merged_obj.__dict__.items():
                    if not key.startswith('_'):
                        setattr(self, key, value)
            return self
        finally:
            session.close()
    
    def delete(self, soft: bool = True):
        """删除实例"""
        if soft:
            self.soft_delete()
            self.save()
        else:
            from app.core.database import get_session
            session = get_session()
            try:
                # 如果对象已经在其他会话中，先合并再删除
                if self not in session:
                    merged_obj = session.merge(self)
                    session.delete(merged_obj)
                else:
                    session.delete(self)
                session.commit()
            finally:
                session.close()
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


# 这些函数现在由 app.core.database 模块提供
# 保留这些函数以保持向后兼容性

def init_database(database_url: str, **engine_options):
    """初始化数据库连接（向后兼容）"""
    from app.core.database import init_database as core_init_database
    return core_init_database(database_url, **engine_options)


def create_tables():
    """创建所有表（向后兼容）"""
    from app.core.database import create_tables as core_create_tables
    return core_create_tables()


def drop_tables():
    """删除所有表"""
    from app.core.database import get_engine
    try:
        engine = get_engine()
        Base.metadata.drop_all(bind=engine)
        logger.info("数据库表删除成功")
    except Exception as e:
        logger.error(f"数据库表删除失败: {e}")
        raise


def get_session() -> Session:
    """获取数据库会话（向后兼容）"""
    from app.core.database import get_session as core_get_session
    return core_get_session()


def close_session():
    """关闭数据库会话（向后兼容）"""
    # 新的设计中每个操作都会自动关闭会话
    pass


# 监听模型更新事件，自动更新updated_at字段
@event.listens_for(BaseModel, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    """更新前自动设置updated_at字段"""
    target.updated_at = datetime.now(timezone.utc)