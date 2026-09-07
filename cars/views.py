# cars/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count  # برای جستجوی پیشرفته
from django.core.paginator import Paginator  # صفحه‌بندی
from django.http import JsonResponse  # پاسخ JSON برای AJAX
from django.contrib.auth.decorators import login_required
from .models import Car, CarImage, Brand, CarModel, Favorite
from .forms import CarForm, CarImageFormSet

class CarListView(ListView):
    """
    نمایش لیست تمام خودروها
    ارث‌بری از ListView Django
    """
    model = Car
    template_name = 'cars/car_list.html'  # تمپلیت
    context_object_name = 'cars'  # نام متغیر در تمپلیت
    paginate_by = 12  # ۱۲ آیتم در هر صفحه
    
    def get_queryset(self):
        """
        فیلتر کردن و مرتب‌سازی داده‌ها
        """
        # ابتدا خودروهای فعال و تاییدشده را بگیر
        queryset = Car.objects.filter(
            is_active=True, 
            is_verified=True
        ).select_related('brand', 'model', 'seller').prefetch_related('images')  # پیش‌بارگیری تصاویر
        
        # 🔹 **فیلترها از GET parameters**
        brand = self.request.GET.get('brand')
        model = self.request.GET.get('model')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        city = self.request.GET.get('city')
        transmission = self.request.GET.get('transmission')
        fuel_type = self.request.GET.get('fuel_type')
        
        # اعمال فیلترها
        if brand:
            queryset = queryset.filter(brand_id=brand)
        if model:
            queryset = queryset.filter(model_id=model)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)  # بزرگتر یا مساوی
        if max_price:
            queryset = queryset.filter(price__lte=max_price)  # کوچکتر یا مساوی
        if city:
            queryset = queryset.filter(city__icontains=city)  # حساس به حروف بزرگ/کوچک نباشد
        if transmission:
            queryset = queryset.filter(transmission=transmission)
        if fuel_type:
            queryset = queryset.filter(fuel_type=fuel_type)
        
        # 🔹 **مرتب‌سازی**
        sort = self.request.GET.get('sort', '-created_at')  # پیش‌فرض: جدیدترین
        if sort in ['price', '-price', 'year', '-year', 'mileage', '-mileage', '-created_at']:
            queryset = queryset.order_by(sort)
        
        return queryset
    

    def get_context_data(self, **kwargs):
        """
        اضافه کردن داده‌های اضافی به context
        """
        context = super().get_context_data(**kwargs)
        
        # ۱۰ برند برتر بر اساس تعداد خودرو
        context['brands'] = Brand.objects.annotate(
            car_count=Count('car')
        ).order_by('-car_count')[:10]
        
        # تعداد کل خودروها
        context['total_cars'] = Car.objects.filter(
            is_active=True, 
            is_verified=True
        ).count()
        
        # لیست انتخاب‌ها برای فیلترها
        context['transmission_choices'] = Car.TRANSMISSION_CHOICES
        context['fuel_choices'] = Car.FUEL_CHOICES
        context['color_choices'] = Car.COLOR_CHOICES
        
        return context
class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'
    
    def get_queryset(self):
        """
        اضافه کردن select_related برای بهینه‌سازی
        این از N+1 query مشکل جلوگیری می‌کنه
        """
        return Car.objects.select_related(
            'seller__profile',  # این خط مهمه - پروفایل رو هم لود کنه
            'brand',
            'model'
        ).prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.get_object()
        
        # 1. افزایش بازدید
        car.views += 1
        car.save(update_fields=['views'])
        
        # 2. بررسی علاقه‌مندی
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                car=car
            ).exists()
        else:
            context['is_favorite'] = False
        
        # 3. خودروهای مشابه (اینجا هم select_related اضافه کنیم)
        context['similar_cars'] = Car.objects.filter(
            brand=car.brand,
            model=car.model,
            is_active=True,
            is_verified=True
        ).exclude(id=car.id).select_related('seller__profile')[:4]
        
        # 4. تصاویر
        context['images'] = car.images.all()
        
        return context
class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'
    
    def form_valid(self, form):
        # تنظیم فروشنده به کاربر جاری
        form.instance.seller = self.request.user
        
        # ابتدا خودرو را ذخیره کن
        self.object = form.save()
        
        # مدیریت تصاویر با Formset
        formset = CarImageFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        
        if formset.is_valid():
            formset.save()
            
            # اگر هیچ تصویری به عنوان اصلی انتخاب نشده
            if not self.object.images.filter(is_main=True).exists():
                first_image = self.object.images.first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()
        else:
            # اگر فرمست معتبر نبود
            return self.form_invalid(form)
        
        messages.success(self.request, 'آگهی شما با موفقیت ثبت شد! پس از تایید نمایش داده می‌شود.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = CarImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = CarImageFormSet()
        
        return context
    
    def form_invalid(self, form):
        # اگر فرم معتبر نبود
        messages.error(self.request, 'لطفا اطلاعات را با دقت پر کنید.')
        return super().form_invalid(form)
class CarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    ویرایش خودرو
    UserPassesTestMixin: بررسی دسترسی کاربر
    """
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'
    
    def test_func(self):
        """
        بررسی آیا کاربر اجازه ویرایش دارد
        """
        car = self.get_object()
        # فقط فروشنده یا مدیر سایت می‌تواند ویرایش کند
        return self.request.user == car.seller or self.request.user.is_staff
    
    def form_valid(self, form):
        formset = CarImageFormSet(
            self.request.POST, 
            self.request.FILES, 
            instance=self.object
        )
        
        if formset.is_valid():
            formset.save()
        
        messages.success(self.request, 'آگهی با موفقیت به‌روزرسانی شد!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = CarImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['formset'] = CarImageFormSet(instance=self.object)
        return context
class CarDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    حذف خودرو
    """
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = '/accounts/my-cars/'  # پس از حذف به کجا برود
    
    def test_func(self):
        car = self.get_object()
        return self.request.user == car.seller
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'آگهی با موفقیت حذف شد!')
        return super().delete(request, *args, **kwargs)

@login_required
def toggle_favorite(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    favorite = Favorite.objects.filter(user=request.user, car=car).first()
    
    if favorite:
        favorite.delete()
        messages.success(request, '❌ از علاقه‌مندی‌ها حذف شد.')
    else:
        Favorite.objects.create(user=request.user, car=car)
        messages.success(request, '✅ به علاقه‌مندی‌ها اضافه شد.')
    
    # برگشت به صفحه قبلی با slug
    return redirect('cars:car_detail', pk=car.id, slug=car.slug)
def get_models(request):
    """
    دریافت مدل‌های یک برند (AJAX)
    """
    brand_id = request.GET.get('brand_id')
    if brand_id:
        models = CarModel.objects.filter(brand_id=brand_id).order_by('name')
        # تبدیل به فرمت JSON
        data = [{'id': m.id, 'name': m.name} for m in models]
        return JsonResponse({'models': data})
    return JsonResponse({'models': []})


# 🔹 **Context Processor**
def brands_processor(request):
    """
    فراهم کردن داده‌ها برای تمام تمپلیت‌ها
    """
    return {
        'all_brands': Brand.objects.all().order_by('name')[:20],
        'featured_cars': Car.objects.filter(
            is_active=True, 
            is_verified=True,
            is_featured=True
        )[:6] if not request.path.startswith('/admin/') else [],
    }