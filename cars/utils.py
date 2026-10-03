from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from .models import Car
from django.conf import settings
from cars.models import Car, Motorcycle, HeavyVehicle

def get_car_statistics():
    """گرفتن آمار خودروها"""
    total_cars = Car.objects.count()
    active_cars = Car.objects.filter(is_active=True, is_verified=True).count()
    sold_cars = Car.objects.filter(is_sold=True).count()
    
    # میانگین قیمت
    avg_price = Car.objects.filter(
        is_active=True, is_verified=True
    ).aggregate(avg=Avg('price'))['avg'] or 0
    
    # آمار ماهانه
    thirty_days_ago = datetime.now() - timedelta(days=30)
    monthly_stats = Car.objects.filter(
        created_at__gte=thirty_days_ago
    ).values('created_at__date').annotate(
        count=Count('id')
    ).order_by('created_at__date')
    
    return {
        'total_cars': total_cars,
        'active_cars': active_cars,
        'sold_cars': sold_cars,
        'avg_price': avg_price,
        'monthly_stats': list(monthly_stats),
    }

def get_popular_brands(limit=10):
    """برندهای محبوب بر اساس تعداد خودرو"""
    return Brand.objects.annotate(
        car_count=Count('car')
    ).order_by('-car_count')[:limit]


def get_user_listings_count(user):
    """
    تعداد کل آگهی‌های (غیر Draft) کاربر
    """
    if not user.is_authenticated:
        return 0
    
    cars_count = Car.objects.filter(seller=user, is_draft=False).count()
    moto_count = Motorcycle.objects.filter(seller=user, is_draft=False).count()
    heavy_count = HeavyVehicle.objects.filter(seller=user, is_draft=False).count()
    
    return cars_count + moto_count + heavy_count


def can_post_free_listing(user):
    """
    آیا کاربر می‌تونه آگهی رایگان ثبت کنه؟
    """
    if not user.is_authenticated:
        return False
    
    free_limit = getattr(settings, 'FREE_LISTINGS_PER_USER', 1)
    current_count = get_user_listings_count(user)
    
    return current_count < free_limit


def get_listing_price(user):
    """
    قیمت آگهی بعدی
    """
    if can_post_free_listing(user):
        return 0
    return getattr(settings, 'LISTING_PRICE', 50000)