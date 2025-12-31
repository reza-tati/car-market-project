# cars/admin.py
from django.contrib import admin
from django.utils.html import format_html  # برای نمایش HTML امن
from .models import Brand, CarModel, Car, CarImage, Favorite

class CarImageInline(admin.TabularInline):
    """
    نمایش تصاویر در صفحه ویرایش خودرو
    """
    model = CarImage
    extra = 1  # یک فرم خالی اضافه کن
    fields = ['image', 'is_main', 'preview']
    readonly_fields = ['preview']  # فقط خواندنی
    
    def preview(self, obj):
        """نمایش تصویر کوچک"""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />', 
                obj.image.url
            )
        return "-"
    preview.short_description = 'پیش‌نمایش'


@admin.register(Car)  # ثبت مدل با دکوراتور
class CarAdmin(admin.ModelAdmin):
    """
    تنظیمات نمایش خودروها در ادمین
    """
    # ستون‌های نمایش داده شده در لیست
    list_display = [
        'id', 'title', 'brand', 'model', 'year', 'price_formatted', 
        'city', 'is_active', 'is_verified', 'is_featured', 'created_at'
    ]
    
    # فیلترهای سمت راست
    list_filter = [
        'brand', 'model', 'year', 'city', 'is_active', 'is_verified', 
        'is_featured', 'created_at'
    ]
    
    # جستجو در این فیلدها
    search_fields = ['title', 'description', 'seller__username', 'seller__email']
    
    # فیلدهای قابل ویرایش در لیست
    list_editable = ['is_active', 'is_verified', 'is_featured']
    
    # فیلدهای فقط خواندنی
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    # نمایش تصاویر در صفحه ویرایش
    inlines = [CarImageInline]
    
    # اکشن‌های دسته‌جمعی
    actions = ['make_verified', 'make_unverified', 'make_featured', 'remove_featured']
    
    # گروه‌بندی فیلدها در صفحه ویرایش
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('seller', 'title', 'brand', 'model', 'year', 'price', 'mileage')
        }),
        ('مشخصات فنی', {
            'fields': ('color', 'transmission', 'fuel_type', 'engine_capacity', 
                      'engine_power', 'condition')
        }),
        ('وضعیت', {
            'fields': ('has_insurance', 'insurance_expiry', 'has_service_book')
        }),
        ('توضیحات و مکان', {
            'fields': ('description', 'city', 'district', 'address')
        }),
        ('وضعیت آگهی', {
            'fields': ('is_sold', 'is_active', 'is_verified', 'is_featured')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)  # قابل جمع شدن
        }),
    )
    
    # 🔹 متدهای کمکی
    def price_formatted(self, obj):
        """فرمت کردن قیمت"""
        return f"{obj.price:,} تومان"
    price_formatted.short_description = 'قیمت'
    
    # 🔹 اکشن‌ها
    def make_verified(self, request, queryset):
        """تایید آگهی‌های انتخاب شده"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} آگهی تایید شد.')
    make_verified.short_description = "تایید آگهی‌های انتخاب شده"
    
    def make_unverified(self, request, queryset):
        """لغو تایید آگهی‌های انتخاب شده"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} آگهی از حالت تایید خارج شد.')
    make_unverified.short_description = "لغو تایید آگهی‌های انتخاب شده"
    
    def make_featured(self, request, queryset):
        """ویژه کردن آگهی‌ها"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} آگهی ویژه شد.')
    make_featured.short_description = "ویژه کردن آگهی‌های انتخاب شده"
    
    def remove_featured(self, request, queryset):
        """حذف از ویژه"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} آگهی از حالت ویژه خارج شد.')
    remove_featured.short_description = "حذف از ویژه"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'car_count']
    search_fields = ['name', 'country']
    
    def car_count(self, obj):
        """تعداد خودروهای این برند"""
        return obj.car_set.count()
    car_count.short_description = 'تعداد خودرو'


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['brand', 'name', 'production_years', 'category']
    list_filter = ['brand', 'category']
    search_fields = ['name', 'brand__name']


# ثبت مدل Favorite
admin.site.register(Favorite)