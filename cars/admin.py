# cars/admin.py
from django.contrib import admin
from .models import (
    Brand, CarModel, Car, Motorcycle, HeavyVehicle,
    CarImage, MotorcycleImage, HeavyVehicleImage, Favorite
)


# ============================================
# برندها و مدل‌ها
# ============================================

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category')
    list_filter = ('brand', 'category')
    search_fields = ('name',)


# ============================================
# خودروها (سواری)
# ============================================

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'city', 'year', 'is_active', 'is_verified', 'is_featured', 'is_sold')
    list_filter = ('is_active', 'is_verified', 'is_featured', 'is_sold', 'year', 'brand')
    list_editable = ('is_verified', 'is_active', 'is_featured', 'is_sold')
    search_fields = ('title', 'description', 'city')
    readonly_fields = ('views', 'phone_views', 'created_at', 'updated_at')
    
    actions = ['approve_cars', 'reject_cars']
    
    def approve_cars(self, request, queryset):
        updated = queryset.update(is_verified=True, is_active=True)
        self.message_user(request, f'{updated} خودرو با موفقیت تأیید شدند.')
    approve_cars.short_description = '✅ تأیید خودروهای انتخاب شده'
    
    def reject_cars(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} خودرو رد شدند.')
    reject_cars.short_description = '❌ رد خودروهای انتخاب شده'


# ============================================
# موتورسیکلت‌ها
# ============================================

@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'city', 'year', 'brand', 'is_active', 'is_verified', 'is_featured')
    list_filter = ('is_active', 'is_verified', 'is_featured', 'brand', 'year')
    list_editable = ('is_verified', 'is_active', 'is_featured')
    search_fields = ('title', 'description', 'city')
    readonly_fields = ('views', 'phone_views', 'created_at', 'updated_at')
    
    actions = ['approve_motorcycles']
    
    def approve_motorcycles(self, request, queryset):
        updated = queryset.update(is_verified=True, is_active=True)
        self.message_user(request, f'{updated} موتورسیکلت تأیید شدند.')
    approve_motorcycles.short_description = '✅ تأیید موتورسیکلت‌های انتخاب شده'


# ============================================
# ماشین‌های سنگین
# ============================================

@admin.register(HeavyVehicle)
class HeavyVehicleAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'city', 'year', 'heavy_type', 'is_active', 'is_verified', 'is_featured')
    list_filter = ('is_active', 'is_verified', 'is_featured', 'heavy_type', 'year')
    list_editable = ('is_verified', 'is_active', 'is_featured')
    search_fields = ('title', 'description', 'city')
    readonly_fields = ('views', 'phone_views', 'created_at', 'updated_at')
    
    actions = ['approve_heavies']
    
    def approve_heavies(self, request, queryset):
        updated = queryset.update(is_verified=True, is_active=True)
        self.message_user(request, f'{updated} ماشین سنگین تأیید شدند.')
    approve_heavies.short_description = '✅ تأیید ماشین‌های سنگین انتخاب شده'


# ============================================
# تصاویر
# ============================================

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'is_main', 'uploaded_at')
    list_filter = ('is_main', 'uploaded_at')
    search_fields = ('car__title',)


@admin.register(MotorcycleImage)
class MotorcycleImageAdmin(admin.ModelAdmin):
    list_display = ('motorcycle', 'is_main', 'uploaded_at')
    list_filter = ('is_main', 'uploaded_at')
    search_fields = ('motorcycle__title',)


@admin.register(HeavyVehicleImage)
class HeavyVehicleImageAdmin(admin.ModelAdmin):
    list_display = ('heavy', 'is_main', 'uploaded_at')
    list_filter = ('is_main', 'uploaded_at')
    search_fields = ('heavy__title',)


# ============================================
# علاقه‌مندی‌ها
# ============================================

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_id', 'vehicle_type', 'created_at')
    list_filter = ('vehicle_type', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)