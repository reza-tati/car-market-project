# accounts/validators.py
"""
Custom validators for user data.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


def iranian_phone_validator(value):
    """
    Validate Iranian mobile phone number.
    
    Valid formats:
    - 09123456789
    - ۰۹۱۲۳۴۵۶۷۸۹
    - +989123456789
    - 989123456789
    """
    if not value:
        return
    
    # Remove any non-digit characters (keep + for now)
    cleaned = re.sub(r'[^\d+]', '', value)
    
    # Convert Persian digits to English
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    translation_table = str.maketrans(persian_digits, english_digits)
    cleaned = cleaned.translate(translation_table)
    
    # Remove + if present
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Check for Iranian mobile prefixes
    if cleaned.startswith('98'):
        cleaned = '0' + cleaned[2:]
    elif cleaned.startswith('0098'):
        cleaned = '0' + cleaned[4:]
    
    # Final validation
    pattern = r'^09[0-9]{9}$'
    
    if not re.match(pattern, cleaned):
        raise ValidationError(
            _('شماره موبایل معتبر نیست. فرمت صحیح: ۰۹۱۲۳۴۵۶۷۸۹'),
            code='invalid_phone'
        )
    
    return cleaned


# Regex validators for common patterns
iranian_mobile_regex = RegexValidator(
    regex=r'^09[0-9]{9}$',
    message='شماره موبایل معتبر نیست. فرمت صحیح: ۰۹۱۲۳۴۵۶۷۸۹',
    code='invalid_phone'
)

persian_name_regex = RegexValidator(
    regex=r'^[\u0600-\u06FF\s]+$',
    message='لطفاً فقط از حروف فارسی استفاده کنید.',
    code='invalid_persian_name'
)

username_regex = RegexValidator(
    regex=r'^[a-zA-Z0-9_\.]+$',
    message='نام کاربری فقط می‌تواند شامل حروف انگلیسی، اعداد، نقطه و زیرخط باشد.',
    code='invalid_username'
)