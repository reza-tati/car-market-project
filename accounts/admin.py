"""from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_seller', 'total_listings')
"""

# Register your models here.
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    """نمایش پروفایل در صفحه کاربر"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'پروفایل'
    fields = ['phone', 'city', 'avatar', 'is_seller', 'seller_rating', 'seller_bio']


class UserAdmin(BaseUserAdmin):
    """سفارشی‌سازی نمایش کاربران"""
    inlines = [UserProfileInline]
    
    # ستون‌های لیست
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_seller']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    
    def is_seller(self, obj):
        """آیا کاربر فروشنده است؟"""
        return obj.profile.is_seller
    is_seller.boolean = True  # نمایش به صورت چک‌باکس
    is_seller.short_description = 'فروشنده'

# ثبت مجدد UserAdmin سفارشی شده
admin.site.unregister(User)
admin.site.register(User, UserAdmin)