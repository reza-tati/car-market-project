# search/views.py
from django.shortcuts import render
from django.db.models import Q  # برای جستجوی OR
from cars.models import Car
from .forms import AdvancedSearchForm

def search_view(request):
    """
    نمایش صفحه جستجو با فیلترها
    """
    form = AdvancedSearchForm(request.GET or None)
    
    # ابتدا همه خودروهای فعال و تاییدشده
    cars = Car.objects.filter(is_active=True, is_verified=True)
    
    if form.is_valid():
        # دریافت داده‌های فرم
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
        
        # 🔹 **اعمال فیلترها**
        
        # جستجوی متن (در چند فیلد)
        if query:
            cars = cars.filter(
                Q(title__icontains=query) |      # در عنوان
                Q(description__icontains=query) | # در توضیحات
                Q(brand__name__icontains=query) | # در نام برند
                Q(model__name__icontains=query)   # در نام مدل
            )
        
        # فیلتر برند
        if brand:
            cars = cars.filter(brand=brand)
        
        # فیلتر مدل
        if model:
            cars = cars.filter(model=model)
        
        # فیلتر سال
        if min_year:
            cars = cars.filter(year__gte=min_year)  # بزرگتر یا مساوی
        
        if max_year:
            cars = cars.filter(year__lte=max_year)  # کوچکتر یا مساوی
        
        # فیلتر قیمت
        if min_price:
            cars = cars.filter(price__gte=min_price)
        
        if max_price:
            cars = cars.filter(price__lte=max_price)
        
        # فیلتر شهر
        if city:
            cars = cars.filter(city__icontains=city)
        
        # فیلتر گیربکس
        if transmission:
            cars = cars.filter(transmission=transmission)
        
        # فیلتر سوخت
        if fuel_type:
            cars = cars.filter(fuel_type=fuel_type)
    
    # 🔹 **مرتب‌سازی**
    sort = request.GET.get('sort', '-created_at')
    if sort in ['price', '-price', 'year', '-year', 'mileage', '-mileage', '-created_at']:
        cars = cars.order_by(sort)
    
    # 🔹 **صفحه‌بندی**
    from django.core.paginator import Paginator
    paginator = Paginator(cars, 12)  # ۱۲ آیتم در صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'cars': page_obj,
        'page_obj': page_obj,
        'total_results': cars.count(),
    }
    
    return render(request, 'search/search.html', context)