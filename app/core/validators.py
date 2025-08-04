"""
数据验证器模块

提供各种数据验证功能
"""

import re
from typing import Any, Dict, List, Optional, Union
from app.core.constants import ConfigDefaults, UserStatus, UserRole
from app.core.exceptions import ValidationError


class BaseValidator:
    """基础验证器类"""
    
    def __init__(self, required: bool = True, allow_none: bool = False):
        self.required = required
        self.allow_none = allow_none
    
    def validate(self, value: Any, field_name: str = "字段") -> Any:
        """验证值"""
        if value is None:
            if self.allow_none:
                return None
            if self.required:
                raise ValidationError(f"{field_name}不能为空")
            return None
        
        return self._validate_value(value, field_name)
    
    def _validate_value(self, value: Any, field_name: str) -> Any:
        """子类需要实现的验证逻辑"""
        return value


class StringValidator(BaseValidator):
    """字符串验证器"""
    
    def __init__(self, min_length: int = 0, max_length: int = None, 
                 pattern: str = None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
    
    def _validate_value(self, value: Any, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串")
        
        if len(value) < self.min_length:
            raise ValidationError(f"{field_name}长度不能少于{self.min_length}个字符")
        
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(f"{field_name}长度不能超过{self.max_length}个字符")
        
        if self.pattern and not self.pattern.match(value):
            raise ValidationError(f"{field_name}格式不正确")
        
        return value.strip()


class EmailValidator(StringValidator):
    """邮箱验证器"""
    
    def __init__(self, **kwargs):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(pattern=email_pattern, max_length=254, **kwargs)
    
    def _validate_value(self, value: Any, field_name: str) -> str:
        value = super()._validate_value(value, field_name)
        return value.lower()


class PasswordValidator(StringValidator):
    """密码验证器"""
    
    def __init__(self, min_length: int = ConfigDefaults.MIN_PASSWORD_LENGTH,
                 max_length: int = ConfigDefaults.MAX_PASSWORD_LENGTH,
                 require_uppercase: bool = True,
                 require_lowercase: bool = True,
                 require_numbers: bool = True,
                 require_symbols: bool = False, **kwargs):
        super().__init__(min_length=min_length, max_length=max_length, **kwargs)
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_symbols = require_symbols
    
    def _validate_value(self, value: Any, field_name: str) -> str:
        value = super()._validate_value(value, field_name)
        
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            raise ValidationError(f"{field_name}必须包含大写字母")
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            raise ValidationError(f"{field_name}必须包含小写字母")
        
        if self.require_numbers and not re.search(r'\d', value):
            raise ValidationError(f"{field_name}必须包含数字")
        
        if self.require_symbols and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError(f"{field_name}必须包含特殊字符")
        
        return value


class IntegerValidator(BaseValidator):
    """整数验证器"""
    
    def __init__(self, min_value: int = None, max_value: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
    
    def _validate_value(self, value: Any, field_name: str) -> int:
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}必须是整数")
        
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"{field_name}不能小于{self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"{field_name}不能大于{self.max_value}")
        
        return value


class EnumValidator(BaseValidator):
    """枚举验证器"""
    
    def __init__(self, enum_class, **kwargs):
        super().__init__(**kwargs)
        self.enum_class = enum_class
        self.valid_values = [item.value for item in enum_class]
    
    def _validate_value(self, value: Any, field_name: str) -> str:
        if value not in self.valid_values:
            raise ValidationError(f"{field_name}必须是以下值之一: {', '.join(self.valid_values)}")
        
        return value


class ListValidator(BaseValidator):
    """列表验证器"""
    
    def __init__(self, item_validator: BaseValidator = None, 
                 min_length: int = 0, max_length: int = None, **kwargs):
        super().__init__(**kwargs)
        self.item_validator = item_validator
        self.min_length = min_length
        self.max_length = max_length
    
    def _validate_value(self, value: Any, field_name: str) -> List[Any]:
        if not isinstance(value, list):
            raise ValidationError(f"{field_name}必须是列表")
        
        if len(value) < self.min_length:
            raise ValidationError(f"{field_name}至少需要{self.min_length}个元素")
        
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(f"{field_name}最多只能有{self.max_length}个元素")
        
        if self.item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_item = self.item_validator.validate(item, f"{field_name}[{i}]")
                    validated_items.append(validated_item)
                except ValidationError as e:
                    raise ValidationError(f"{field_name}第{i+1}个元素验证失败: {e.message}")
            return validated_items
        
        return value


class DictValidator(BaseValidator):
    """字典验证器"""
    
    def __init__(self, schema: Dict[str, BaseValidator], **kwargs):
        super().__init__(**kwargs)
        self.schema = schema
    
    def _validate_value(self, value: Any, field_name: str) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name}必须是字典")
        
        validated_data = {}
        errors = {}
        
        # 验证每个字段
        for key, validator in self.schema.items():
            try:
                validated_data[key] = validator.validate(value.get(key), key)
            except ValidationError as e:
                errors[key] = e.message
        
        if errors:
            raise ValidationError(f"{field_name}验证失败", details=errors)
        
        return validated_data


# 预定义的验证器实例
username_validator = StringValidator(min_length=3, max_length=50, 
                                   pattern=r'^[a-zA-Z0-9_]+$')
email_validator = EmailValidator()
password_validator = PasswordValidator()
user_status_validator = EnumValidator(UserStatus)
user_role_validator = EnumValidator(UserRole)
page_validator = IntegerValidator(min_value=1)
page_size_validator = IntegerValidator(min_value=1, max_value=ConfigDefaults.MAX_PAGE_SIZE)


def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证用户数据"""
    schema = {
        'username': username_validator,
        'email': email_validator,
        'password': password_validator,
        'full_name': StringValidator(min_length=1, max_length=100),
        'status': EnumValidator(UserStatus, required=False),
        'role': EnumValidator(UserRole, required=False)
    }
    
    validator = DictValidator(schema)
    return validator.validate(data, "用户数据")


def validate_pagination_params(page: Any = 1, page_size: Any = ConfigDefaults.DEFAULT_PAGE_SIZE) -> Dict[str, int]:
    """验证分页参数"""
    return {
        'page': page_validator.validate(page, '页码'),
        'page_size': page_size_validator.validate(page_size, '每页数量')
    }