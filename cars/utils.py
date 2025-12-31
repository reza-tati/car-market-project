# cars/utils.py (ایجاد فایل جدید)
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from .models import Car

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