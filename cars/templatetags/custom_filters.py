# cars/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def intcomma(value):
    """فرمت اعداد با جداکننده هزارگان"""
    try:
        value = int(value)
        # جداکننده فارسی
        return f"{value:,}".replace(',', '٬')
    except (ValueError, TypeError):
        return str(value)