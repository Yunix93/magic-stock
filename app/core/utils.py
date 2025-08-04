"""
工具函数模块

提供通用的工具函数
"""

import uuid
import hashlib
import secrets
import string
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.constants import DateFormats
import logging

logger = logging.getLogger(__name__)


def generate_uuid() -> str:
    """生成UUID字符串"""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """生成短ID"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str) -> str:
    """密码哈希"""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return check_password_hash(password_hash, password)


def generate_secure_token(length=32):
    """生成安全令牌"""
    return secrets.token_urlsafe(length)


def get_current_timestamp():
    """获取当前时间戳"""
    return datetime.now(timezone.utc)


def format_datetime(dt: Optional[datetime], format_str: str = DateFormats.DATETIME) -> Optional[str]:
    """格式化日期时间"""
    if dt is None:
        return None
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = DateFormats.DATETIME) -> Optional[datetime]:
    """解析日期时间字符串"""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def sanitize_filename(filename):
    """清理文件名，移除不安全字符"""
    import re
    # 移除路径分隔符和其他不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 移除控制字符
    filename = ''.join(char for char in filename if ord(char) >= 32)
    # 限制长度
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    return filename


def calculate_file_hash(file_path, algorithm='sha256'):
    """计算文件哈希值"""
    hash_func = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logger.error(f"计算文件哈希失败: {e}")
        return None


def validate_phone(phone):
    """验证手机号格式（中国大陆）"""
    import re
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def mask_sensitive_data(data, mask_char='*', visible_chars=4):
    """遮蔽敏感数据"""
    if not data or len(data) <= visible_chars:
        return data
    
    visible_start = visible_chars // 2
    visible_end = visible_chars - visible_start
    
    if visible_end == 0:
        return data[:visible_start] + mask_char * (len(data) - visible_start)
    else:
        return (data[:visible_start] + 
                mask_char * (len(data) - visible_chars) + 
                data[-visible_end:])


def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """分页查询辅助函数"""
    # 限制每页数量
    per_page = min(per_page, max_per_page)
    
    # 计算偏移量
    offset = (page - 1) * per_page
    
    # 获取总数
    total = query.count()
    
    # 获取当前页数据
    items = query.offset(offset).limit(per_page).all()
    
    # 计算分页信息
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_page': page - 1 if has_prev else None,
        'next_page': page + 1 if has_next else None
    }


def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """安全转换为浮点数"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_string(text, length=100, suffix='...'):
    """截断字符串"""
    if not text or len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def get_client_ip(request):
    """获取客户端IP地址"""
    # 检查代理头
    forwarded_ips = request.headers.get('X-Forwarded-For')
    if forwarded_ips:
        return forwarded_ips.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.remote_addr


def is_safe_url(target, host):
    """检查URL是否安全（防止开放重定向）"""
    from urllib.parse import urlparse, urljoin
    
    ref_url = urlparse(urljoin(host, target))
    test_url = urlparse(urljoin(host, '/'))
    
    return ref_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc