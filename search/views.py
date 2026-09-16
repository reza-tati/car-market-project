# search/views.py
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from itertools import chain
from .forms import AdvancedSearchForm
from cars.models import Car, Motorcycle, HeavyVehicle, Favorite, Brand


def search_view(request):
    """
    نمایش صفحه جستجو با فیلترها (سواری، موتورسیکلت، سنگین)
    """
    form = AdvancedSearchForm(request.GET or None)
    
    # همه وسایل نقلیه فعال و تاییدشده
    cars = Car.objects.filter(is_active=True, is_verified=True)
    motorcycles = Motorcycle.objects.filter(is_active=True, is_verified=True)
    heavies = HeavyVehicle.objects.filter(is_active=True, is_verified=True)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        brand = form.cleaned_data.get('brand')
        model = form.cleaned_data.get('model')
        min_year = form.cleaned_data.get('min_year')
        max_year = form.cleaned_data.get('max_year')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        city = form.cleaned_data.get('city')
        transmission = form.cleaned_data.get('transmission')
        fuel_type = form.cleaned_data.get('fuel_type')
        
        # ===== جستجوی متن در هر سه مدل =====
        if query:
            cars = cars.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(model__name__icontains=query)
            )
            motorcycles = motorcycles.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query) |
                Q(model_name__icontains=query)
            )
            heavies = heavies.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query) |
                Q(model_name__icontains=query)
            )
        
        # ===== فیلتر برند =====
        # ✅ اگه برند انتخاب شده، فقط سواری‌ها فیلتر میشن
        # چون موتور و سنگین برندشون متن (CharField) هست نه FK
        if brand:
            cars = cars.filter(brand=brand)
            brand_name=brand.name
            motorcycles = motorcycles.filter(brand__iexact=brand.name)
            heavies = heavies.filter(brand__iexact=brand.name)
        
        # ===== فیلتر مدل (فقط سواری) =====
        if model:
            cars = cars.filter(model=model)
        
        # ===== فیلتر سال =====
        if min_year:
            cars = cars.filter(year__gte=min_year)
            motorcycles = motorcycles.filter(year__gte=min_year)
            heavies = heavies.filter(year__gte=min_year)
        
        if max_year:
            cars = cars.filter(year__lte=max_year)
            motorcycles = motorcycles.filter(year__lte=max_year)
            heavies = heavies.filter(year__lte=max_year)
        
        # ===== فیلتر قیمت =====
        if min_price:
            cars = cars.filter(price__gte=min_price)
            motorcycles = motorcycles.filter(price__gte=min_price)
            heavies = heavies.filter(price__gte=min_price)
        
        if max_price:
            cars = cars.filter(price__lte=max_price)
            motorcycles = motorcycles.filter(price__lte=max_price)
            heavies = heavies.filter(price__lte=max_price)
        
        # ===== فیلتر شهر =====
        if city:
            cars = cars.filter(city__icontains=city)
            motorcycles = motorcycles.filter(city__icontains=city)
            heavies = heavies.filter(city__icontains=city)
        
        # ===== فیلتر گیربکس (فقط سواری) =====
        if transmission:
            cars = cars.filter(transmission=transmission)
            # موتور و سنگین گیربکس ندارن، پس اگه گیربکس انتخاب شده
            # اون‌ها رو خالی کن
            motorcycles = motorcycles.none()
            heavies = heavies.none()
        
        # ===== فیلتر سوخت (فقط سواری) =====
        if fuel_type:
            cars = cars.filter(fuel_type=fuel_type)
            # موتور و سنگین نوع سوخت ندارن
            motorcycles = motorcycles.none()
            heavies = heavies.none()
    
    # ===== ترکیب همه =====
    all_vehicles = list(chain(cars, motorcycles, heavies))
    
    # ===== مرتب‌سازی =====
    sort = request.GET.get('sort', '-created_at')
    if sort == 'price':
        all_vehicles.sort(key=lambda x: x.price)
    elif sort == '-price':
        all_vehicles.sort(key=lambda x: x.price, reverse=True)
    elif sort == 'year':
        all_vehicles.sort(key=lambda x: x.year)
    elif sort == '-year':
        all_vehicles.sort(key=lambda x: x.year, reverse=True)
    elif sort == 'mileage':
        all_vehicles.sort(key=lambda x: getattr(x, 'mileage', 0))
    else:  # -created_at (پیش‌فرض)
        all_vehicles.sort(key=lambda x: x.created_at, reverse=True)
    
    # ===== صفحه‌بندی =====
    paginator = Paginator(all_vehicles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # ===== favorite_ids =====
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(
            user=request.user
        ).values_list('vehicle_id', flat=True))
    else:
        favorite_ids = []
    
    context = {
        'form': form,
        'cars': page_obj,
        'page_obj': page_obj,
        'total_results': len(all_vehicles),
        'favorite_ids': favorite_ids,
        'all_brands': Brand.objects.all().order_by('name'), 
    }
    
    return render(request, 'search/search.html', context)