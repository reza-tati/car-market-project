# cars/templatetags/custom_filters.py
from django import template
from cars.models import Favorite  # اضافه کردن ایمپورت
_DIGIT_MAP = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
register = template.Library()

@register.filter
def intcomma(value):
    """عدد با جداکننده هزارگان و ارقام فارسی: 1234567 → ۱٬۲۳۴٬۵۶۷"""
    try:
        formatted = '{:,}'.format(int(value))
    except (ValueError, TypeError):
        return value
    return formatted.replace(',', '٬').translate(_DIGIT_MAP)

@register.filter
def is_favorited_by(vehicle, user):
    """
    بررسی اینکه آیا کاربر این آگهی را پسندیده است
    استفاده: {% if car|is_favorited_by:request.user %}
    """
    if not user or not user.is_authenticated:
        return False
    return Favorite.objects.filter(
        user=user,
        vehicle_id=vehicle.id,
        vehicle_type=vehicle.vehicle_type,   # ← خود آگهی نوعش رو می‌گه!
    ).exists()

@register.filter
def truncatechars_fa(value, arg):
    """
    کوتاه کردن متن و اضافه کردن سه نقطه فارسی
    arg: تعداد کاراکترها
    """
    try:
        length = int(arg)
        if len(str(value)) > length:
            return str(value)[:length] + "…"  # سه نقطه فارسی
        return str(value)
    except (ValueError, TypeError):
        return str(value)


@register.filter
def get_choice_display(obj, field_name):
    """
    دریافت نمایش فارسی یک فیلد choice
    """
    if hasattr(obj, f'get_{field_name}_display'):
        return getattr(obj, f'get_{field_name}_display')()
    return getattr(obj, field_name, '')

@register.filter
def fa_digits(value):
    """تبدیل همه ارقام انگلیسی یک متن به فارسی: 3 روز → ۳ روز"""
    return str(value).translate(_DIGIT_MAP)