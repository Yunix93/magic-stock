"""
配置管理模块

提供不同环境的配置类和配置加载功能
"""

from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

__all__ = [
    'config',
    'BaseConfig',
    'DevelopmentConfig', 
    'ProductionConfig',
    'TestingConfig'
]