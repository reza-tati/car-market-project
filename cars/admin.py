# cars/admin.py
from django.contrib import admin
from .models import (
    Brand, CarModel, Car, Motorcycle, HeavyVehicle,
    CarImage, MotorcycleImage, HeavyVehicleImage, Favorite, VehicleCatalogModel, VehicleVariant
)
from datetime import date, datetime

from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import path

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
    change_list_template = "admin/cars/car/change_list.html"

    def approve_cars(self, request, queryset):
        updated = queryset.update(is_verified=True, is_active=True)
        self.message_user(request, f'{updated} خودرو با موفقیت تأیید شدند.')
    approve_cars.short_description = '✅ تأیید خودروهای انتخاب شده'
    
    def reject_cars(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} خودرو رد شدند.')
    reject_cars.short_description = '❌ رد خودروهای انتخاب شده'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "all-ads/",
                self.admin_site.admin_view(self.all_ads_view),
                name="cars_car_unified_ads",
            ),
            path(
                "approve/<str:vehicle_type>/<int:pk>/",
                self.admin_site.admin_view(self.approve_ad_view),
                name="cars_car_approve_ad",
            ),
        ]
        return custom_urls + urls


    def all_ads_view(self, request):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied

        vehicle_models = [
            (Car, "سواری"),
            (Motorcycle, "موتورسیکلت"),
            (HeavyVehicle, "ماشین سنگین"),
        ]

        ads = []

        for model_class, type_label in vehicle_models:
            for obj in model_class.objects.filter(
                    is_verified=False,
                    is_draft=False,
                    is_sold=False,
                ):
                created = getattr(obj, "created_at", None)

                if isinstance(created, datetime):
                    sort_value = created.timestamp()
                elif isinstance(created, date):
                    sort_value = created.toordinal() * 86400
                else:
                    # اگر مدل فیلد تاریخ ثبت نداشته باشد، از شناسه به‌عنوان ترتیب تقریبی استفاده می‌شود.
                    sort_value = obj.pk

                model_info = (
                    getattr(obj, "catalog_model", None)
                    or getattr(obj, "model", None)
                    or getattr(obj, "model_name", "")
                )

                if getattr(obj, "is_draft", False):
                    status = "پیش‌نویس"
                elif getattr(obj, "is_sold", False):
                    status = "فروخته‌شده"
                elif not getattr(obj, "is_active", False):
                    status = "در انتظار تأیید"
                else:
                    status = "فعال"


                change_url = reverse(
                    f"admin:{model_class._meta.app_label}_"
                    f"{model_class._meta.model_name}_change",
                    args=[obj.pk],
                )

                ads.append({
                    "type": type_label,
                    "title": getattr(obj, "title", str(obj)),
                    "model": str(model_info),
                    "price": getattr(obj, "price", ""),
                    "city": str(getattr(obj, "city", "")),
                    "status": status,
                    "created": created,
                    "sort_value": sort_value,
                    "change_url": change_url,
                    "approve_url": reverse(
                        "admin:cars_car_approve_ad",
                        args=[
                            "car" if model_class == Car
                            else "motorcycle" if model_class == Motorcycle
                            else "heavy",
                            obj.pk,
                        ],
                    ),
                })

        ads.sort(key=lambda ad: ad["sort_value"], reverse=True)
        page_obj = Paginator(ads, 30).get_page(request.GET.get("page"))

        context = {
            **self.admin_site.each_context(request),
            "title": "همه آگهی‌ها",
            "opts": self.model._meta,
            "page_obj": page_obj,
        }
        return TemplateResponse(request, "admin/cars/unified_ads.html", context)
    
    def approve_ad_view(self, request, vehicle_type, pk):
        if request.method != "POST":
            raise PermissionDenied

        vehicle_models = {
            "car": Car,
            "motorcycle": Motorcycle,
            "heavy": HeavyVehicle,
        }

        model_class = vehicle_models.get(vehicle_type)
        if model_class is None:
            raise PermissionDenied

        permission = (
            f"{model_class._meta.app_label}."
            f"change_{model_class._meta.model_name}"
        )
        if not request.user.has_perm(permission):
            raise PermissionDenied

        vehicle = get_object_or_404(
            model_class,
            pk=pk,
            is_verified=False,
            is_draft=False,
            is_sold=False,
        )

        vehicle.is_verified = True
        vehicle.is_active = True
        vehicle.is_draft = False
        vehicle.save(update_fields=[
            "is_verified",
            "is_active",
            "is_draft",
        ])

        messages.success(request, "آگهی تأیید و منتشر شد.")
        return redirect("admin:cars_car_unified_ads")


# ============================================
# موتورسیکلت‌ها
# ============================================

@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'city', 'year', 'brand', 'is_active', 'is_verified', 'is_featured', 'is_sold')
    list_filter = ('is_active', 'is_verified', 'is_featured', 'brand', 'year')
    list_editable = ('is_verified', 'is_active', 'is_featured', 'is_sold')
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
    list_display = ('title', 'price', 'city', 'year', 'heavy_type', 'is_active', 'is_verified', 'is_featured', 'is_sold')
    list_filter = ('is_active', 'is_verified', 'is_featured', 'heavy_type', 'year')
    list_editable = ('is_verified', 'is_active', 'is_featured', 'is_sold')
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

class VehicleVariantInline(admin.TabularInline):
    model = VehicleVariant
    extra = 1


@admin.register(VehicleCatalogModel)
class VehicleCatalogModelAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'brand',
        'vehicle_type',
        'category',
        'is_current',
        'is_active',
    )
    list_filter = ('vehicle_type', 'brand', 'is_current', 'is_active')
    search_fields = ('name', 'brand__name')
    inlines = (VehicleVariantInline,)


@admin.register(VehicleVariant)
class VehicleVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'catalog_model', 'production_start_year', 'production_end_year', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'catalog_model__name', 'catalog_model__brand__name')
