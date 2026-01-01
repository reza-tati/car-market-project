# cars/templatetags/custom_filters.py
from django import template
from cars.models import Favorite  # اضافه کردن ایمپورت

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


@register.filter
def is_favorited_by(car, user):
    """
    فیلتر template برای بررسی آیا کاربر خودرو را پسندیده است
    
    استفاده در تمپلیت:
    {% if car|is_favorited_by:user %}
    """
    # بررسی اگر کاربر لاگین نکرده
    if not user or not user.is_authenticated:
        return False
    
    # بررسی وجود رکورد در جدول Favorite
    # روش ۱: استفاده از exists() برای کارایی بهتر
    return Favorite.objects.filter(car=car, user=user).exists()
    
    # روش ۲: استفاده از related_name (اگر می‌خواهید از رابطه استفاده کنید)
    # return car.favorited_by.filter(user=user).exists()


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