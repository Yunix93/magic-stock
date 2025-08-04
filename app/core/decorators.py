"""
装饰器模块

提供各种功能装饰器
"""

import time
import functools
from flask import request, jsonify
from app.core.exceptions import RateLimitError
from app.core.constants import HTTPStatus, APIMessages
import logging

logger = logging.getLogger(__name__)


def log_execution_time(func):
    """记录函数执行时间的装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 执行时间: {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败 (耗时: {execution_time:.3f}s): {e}")
            raise
    return wrapper


def handle_exceptions(func):
    """统一异常处理装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"函数 {func.__name__} 发生异常: {e}", exc_info=True)
            # 根据异常类型返回不同的响应
            if hasattr(e, 'to_dict'):
                return jsonify(e.to_dict()), getattr(e, 'status_code', HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                return jsonify({
                    'error': 'InternalServerError',
                    'message': APIMessages.INTERNAL_ERROR,
                    'details': str(e) if logger.level <= logging.DEBUG else {}
                }), HTTPStatus.INTERNAL_SERVER_ERROR
    return wrapper


def validate_json(required_fields=None):
    """JSON数据验证装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'InvalidRequest',
                    'message': '请求必须是JSON格式'
                }), HTTPStatus.BAD_REQUEST
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'InvalidRequest',
                    'message': '请求体不能为空'
                }), HTTPStatus.BAD_REQUEST
            
            # 检查必需字段
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': 'ValidationError',
                        'message': f'缺少必需字段: {", ".join(missing_fields)}'
                    }), HTTPStatus.BAD_REQUEST
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cache_result(timeout=300, key_func=None):
    """结果缓存装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from app.core.extensions import cache
            
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取结果
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            logger.debug(f"结果已缓存: {cache_key}")
            
            return result
        return wrapper
    return decorator


def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """重试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"{func.__name__} 重试 {max_attempts} 次后仍然失败: {e}")
                        raise
                    
                    logger.warning(f"{func.__name__} 第 {attempts} 次尝试失败，{current_delay}s 后重试: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator