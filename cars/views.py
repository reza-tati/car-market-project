# cars/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from itertools import chain

from .models import (
    Car, Motorcycle, HeavyVehicle,
    CarImage, MotorcycleImage, HeavyVehicleImage,
    Brand, CarModel, Favorite,
)
from .forms import (
    CarForm, MotorcycleForm, HeavyVehicleForm,
    CarImageFormSet, MotorcycleImageFormSet, HeavyVehicleImageFormSet,
)

# ============================================
# لیست خودروها (سواری)
# ============================================

class CarListView(ListView):
    template_name = 'cars/car_list.html'
    context_object_name = 'cars'
    paginate_by = 12
    
    def get_queryset(self):
        # ===== ۱. دریافت نوع فیلتر از URL =====
        vehicle_type = self.request.GET.get('type', 'all')
        
        # ===== ۲. دریافت وسایل نقلیه بر اساس نوع =====
        if vehicle_type == 'car':
            # فقط سواری
            cars = Car.objects.filter(is_active=True, is_verified=True).select_related('brand', 'model', 'seller').prefetch_related('car_images')
            all_vehicles = list(cars)
            
        elif vehicle_type == 'motorcycle':
            # فقط موتورسیکلت
            motorcycles = Motorcycle.objects.filter(is_active=True, is_verified=True).select_related('seller').prefetch_related('motorcycle_images')
            all_vehicles = list(motorcycles)
            
        elif vehicle_type == 'heavy':
            # فقط ماشین سنگین
            heavies = HeavyVehicle.objects.filter(is_active=True, is_verified=True).select_related('seller').prefetch_related('heavy_images')
            all_vehicles = list(heavies)
            
        else:
            # همه وسایل نقلیه (پیش‌فرض)
            cars = Car.objects.filter(is_active=True, is_verified=True).select_related('brand', 'model', 'seller').prefetch_related('car_images')
            motorcycles = Motorcycle.objects.filter(is_active=True, is_verified=True).select_related('seller').prefetch_related('motorcycle_images')
            heavies = HeavyVehicle.objects.filter(is_active=True, is_verified=True).select_related('seller').prefetch_related('heavy_images')
            
            all_vehicles = sorted(
                chain(cars, motorcycles, heavies),
                key=lambda x: x.created_at,
                reverse=True
            )
        
        # ===== ۳. اعمال فیلترها (فقط برای سواری معنی‌داره) =====
        brand = self.request.GET.get('brand')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        city = self.request.GET.get('city')
        
        if vehicle_type == 'car' and brand:
            all_vehicles = [v for v in all_vehicles if v.brand_id == int(brand)]
        
        if min_price:
            all_vehicles = [v for v in all_vehicles if v.price >= int(min_price)]
        
        if max_price:
            all_vehicles = [v for v in all_vehicles if v.price <= int(max_price)]
        
        if city:
            all_vehicles = [v for v in all_vehicles if city.lower() in v.city.lower()]
        
        # ===== ۴. صفحه‌بندی دستی =====
        from django.core.paginator import Paginator
        paginator = Paginator(all_vehicles, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        self.page_obj = page_obj
        
        return page_obj.object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ===== ۱. اضافه کردن page_obj برای صفحه‌بندی =====
        if hasattr(self, 'page_obj'):
            context['page_obj'] = self.page_obj
            context['is_paginated'] = self.page_obj.has_other_pages()
        
        # ===== ۲. اضافه کردن favorite_ids =====
        if self.request.user.is_authenticated:
            context['favorite_ids'] = list(Favorite.objects.filter(
                user=self.request.user
            ).values_list('vehicle_id', flat=True))
        else:
            context['favorite_ids'] = []
        
        # ===== ۳. برندها با تعداد خودرو =====
        context['brands'] = Brand.objects.annotate(
            car_count=Count('car')
        ).filter(car_count__gt=0).order_by('-car_count')[:10]
        
        # ===== ۴. آمار کلی =====
        context['total_cars'] = Car.objects.filter(
            is_active=True, is_verified=True
        ).count()
        context['total_motorcycles'] = Motorcycle.objects.filter(
            is_active=True, is_verified=True
        ).count()
        context['total_heavies'] = HeavyVehicle.objects.filter(
            is_active=True, is_verified=True
        ).count()
        
        # ===== ۵. انتخاب‌ها برای فیلترها =====
        context['transmission_choices'] = Car.TRANSMISSION_CHOICES
        context['fuel_choices'] = Car.FUEL_CHOICES
        context['color_choices'] = Car.COLOR_CHOICES
        
        return context

# ============================================
# لیست موتورسیکلت‌ها
# ============================================
class MotorcycleListView(ListView):
    model = Motorcycle
    template_name = 'cars/motorcycle_list.html'
    context_object_name = 'motorcycles'
    paginate_by = 12
    
    def get_queryset(self):
        return Motorcycle.objects.filter(
            is_active=True, 
            is_verified=True
        ).select_related('seller').prefetch_related('motorcycle_images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['favorite_ids'] = Favorite.objects.filter(
                user=self.request.user
            ).values_list('vehicle_id', flat=True)
        else:
            context['favorite_ids'] = []
        return context


# ============================================
# لیست ماشین‌های سنگین
# ============================================
class HeavyVehicleListView(ListView):
    model = HeavyVehicle
    template_name = 'cars/heavy_list.html'
    context_object_name = 'heavies'
    paginate_by = 12
    
    def get_queryset(self):
        return HeavyVehicle.objects.filter(
            is_active=True, 
            is_verified=True
        ).select_related('seller').prefetch_related('heavy_images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['favorite_ids'] = Favorite.objects.filter(
                user=self.request.user
            ).values_list('vehicle_id', flat=True)
        else:
            context['favorite_ids'] = []
        return context


# ============================================
# جزئیات خودرو (سواری)
# ============================================
class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'
    
    def get_queryset(self):
        return Car.objects.select_related(
            'seller__profile', 'brand', 'model'
        ).prefetch_related('car_images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.get_object()
        
        # افزایش بازدید
        car.views += 1
        car.save(update_fields=['views'])
        
        # بررسی علاقه‌مندی
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                vehicle_id=car.id,
                vehicle_type='car'
            ).exists()
        else:
            context['is_favorite'] = False
        
        # ✅ خودروهای مشابه: اول هم‌برند و هم‌مدل، بعد هم‌برند
        similar_cars = Car.objects.filter(
            brand=car.brand,
            model=car.model,
            is_active=True,
            is_verified=True
        ).exclude(id=car.id)[:4]

        # اگه کمتر از ۴ تا بود، از هم‌برندها پر کن
        if similar_cars.count() < 4:
            more_cars = Car.objects.filter(
                brand=car.brand,
                is_active=True,
                is_verified=True
            ).exclude(id=car.id).exclude(
                id__in=similar_cars.values_list('id', flat=True)
            )[:4 - similar_cars.count()]
            
            similar_cars = list(similar_cars) + list(more_cars)

        # اگه بازم کمتر از ۴ تا بود، از همه خودروها پر کن
        if len(similar_cars) < 4:
            more_cars = Car.objects.filter(
                is_active=True,
                is_verified=True
            ).exclude(id=car.id).exclude(
                id__in=[c.id for c in similar_cars]
            )[:4 - len(similar_cars)]
            
            similar_cars = list(similar_cars) + list(more_cars)

        context['similar_cars'] = similar_cars
        context['images'] = car.car_images.all()
        
        return context


# ============================================
# جزئیات موتورسیکلت
# ============================================
class MotorcycleDetailView(DetailView):
    model = Motorcycle
    template_name = 'cars/motorcycle_detail.html'
    context_object_name = 'motorcycle'
    
    def get_queryset(self):
        return Motorcycle.objects.select_related('seller__profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        motorcycle = self.get_object()
        
        motorcycle.views += 1
        motorcycle.save(update_fields=['views'])
        
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                vehicle_id=motorcycle.id,
                vehicle_type='motorcycle'
            ).exists()
        else:
            context['is_favorite'] = False
        
        context['images'] = motorcycle.motorcycle_images.all()
        
        return context


# ============================================
# جزئیات ماشین سنگین
# ============================================
class HeavyVehicleDetailView(DetailView):
    model = HeavyVehicle
    template_name = 'cars/heavy_detail.html'
    context_object_name = 'heavy'
    
    def get_queryset(self):
        return HeavyVehicle.objects.select_related('seller__profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        heavy = self.get_object()
        
        heavy.views += 1
        heavy.save(update_fields=['views'])
        
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                vehicle_id=heavy.id,
                vehicle_type='heavy'
            ).exists()
        else:
            context['is_favorite'] = False
        
        context['images'] = heavy.heavy_images.all()
        
        return context


# ============================================
# ایجاد خودرو (سواری)
# ============================================
class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'
    
    def form_valid(self, form):
        print("=" * 60)
        print("✅ form_valid CALLED")
        print(f"FILES: {self.request.FILES}")
        
        form.instance.seller = self.request.user
        form.instance.vehicle_type = 'car'
        self.object = form.save()
        
        print(f"✅ Car saved with ID: {self.object.id}")
        
        formset = CarImageFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        
        print(f"formset.is_valid(): {formset.is_valid()}")
        print(f"formset.errors: {formset.errors}")
        print(f"formset.non_form_errors(): {formset.non_form_errors()}")
        
        if formset.is_valid():
            formset.save()
            print(f"✅ Images saved!")
            
            if not self.object.car_images.filter(is_main=True).exists():
                first_image = self.object.car_images.first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()
                    print(f"✅ Main image set")
        else:
            print(f"❌ Formset invalid!")
            return self.form_invalid(form)
        
        messages.success(self.request, 'آگهی شما با موفقیت ثبت شد!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print("=" * 60)
        print("❌ form_invalid CALLED")
        print(f"Form errors: {form.errors}")
        print("=" * 60)
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = CarImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = CarImageFormSet()
        return context



# ============================================
# ایجاد موتورسیکلت
# ============================================
class MotorcycleCreateView(LoginRequiredMixin, CreateView):
    model = Motorcycle
    form_class = MotorcycleForm
    template_name = 'cars/motorcycle_form.html'
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.vehicle_type = 'motorcycle'
        self.object = form.save()
        
        formset = MotorcycleImageFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        
        if formset.is_valid():
            formset.save()
            
            if not self.object.motorcycle_images.filter(is_main=True).exists():
                first_image = self.object.motorcycle_images.first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()
        else:
            return self.form_invalid(form)
        
        messages.success(self.request, 'موتورسیکلت با موفقیت ثبت شد!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = MotorcycleImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = MotorcycleImageFormSet()
        return context
    
    def form_invalid(self, form):
        messages.error(self.request, 'لطفا اطلاعات را با دقت پر کنید.')
        return super().form_invalid(form)



# ============================================
# ایجاد ماشین سنگین
# ============================================
class HeavyVehicleCreateView(LoginRequiredMixin, CreateView):
    model = HeavyVehicle
    form_class = HeavyVehicleForm
    template_name = 'cars/heavy_form.html'
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.vehicle_type = 'heavy'
        self.object = form.save()
        
        formset = HeavyVehicleImageFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        
        if formset.is_valid():
            formset.save()
            
            if not self.object.heavy_images.filter(is_main=True).exists():
                first_image = self.object.heavy_images.first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()
        else:
            return self.form_invalid(form)
        
        messages.success(self.request, 'ماشین سنگین با موفقیت ثبت شد!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = HeavyVehicleImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = HeavyVehicleImageFormSet()
        return context
    
    def form_invalid(self, form):
        messages.error(self.request, 'لطفا اطلاعات را با دقت پر کنید.')
        return super().form_invalid(form)



# ============================================
# ویرایش خودرو
# ============================================
class CarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'cars/car_form.html'
    
    def test_func(self):
        car = self.get_object()
        return self.request.user == car.seller or self.request.user.is_staff
    
    def form_valid(self, form):
        self.object = form.save()
        
        formset = CarImageFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        
        if formset.is_valid():
            formset.save()
            
            if not self.object.car_images.filter(is_main=True).exists():
                first_image = self.object.car_images.first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()
        else:
            return self.form_invalid(form)
        
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

# ============================================
# حذف خودرو
# ============================================
class CarDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = '/accounts/my-cars/'
    
    def test_func(self):
        car = self.get_object()
        return self.request.user == car.seller

# ============================================
# ویرایش موتورسیکلت
# ============================================
class MotorcycleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Motorcycle
    form_class = MotorcycleForm
    template_name = 'cars/motorcycle_form.html'
    
    def test_func(self):
        motorcycle = self.get_object()
        return self.request.user == motorcycle.seller or self.request.user.is_staff
    
    def form_valid(self, form):
        self.object = form.save()
        
        formset = MotorcycleImageFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        
        if formset.is_valid():
            formset.save()
            
            if not self.object.motorcycle_images.filter(is_main=True).exists():
                first_image = self.object.motorcycle_images.first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()
        else:
            return self.form_invalid(form)
        
        messages.success(self.request, 'موتورسیکلت با موفقیت به‌روزرسانی شد!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = MotorcycleImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['formset'] = MotorcycleImageFormSet(instance=self.object)
        return context
# ============================================
# حذف موتورسیکلت
# ============================================
class MotorcycleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Motorcycle
    template_name = 'cars/motorcycle_confirm_delete.html'
    success_url = '/accounts/my-cars/'
    
    def test_func(self):
        motorcycle = self.get_object()
        return self.request.user == motorcycle.seller


# ============================================
# ویرایش ماشین سنگین
# ============================================
class HeavyVehicleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HeavyVehicle
    form_class = HeavyVehicleForm
    template_name = 'cars/heavy_form.html'
    
    def test_func(self):
        heavy = self.get_object()
        return self.request.user == heavy.seller or self.request.user.is_staff
    
    def form_valid(self, form):
        self.object = form.save()
        
        formset = HeavyVehicleImageFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        
        if formset.is_valid():
            formset.save()
            
            if not self.object.heavy_images.filter(is_main=True).exists():
                first_image = self.object.heavy_images.first()
                if first_image:
                    first_image.is_main = True
                    first_image.save()
        else:
            return self.form_invalid(form)
        
        messages.success(self.request, 'ماشین سنگین با موفقیت به‌روزرسانی شد!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = HeavyVehicleImageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['formset'] = HeavyVehicleImageFormSet(instance=self.object)
        return context

# ============================================
# حذف ماشین سنگین
# ============================================
class HeavyVehicleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = HeavyVehicle
    template_name = 'cars/heavy_confirm_delete.html'
    success_url = '/accounts/my-cars/'
    
    def test_func(self):
        heavy = self.get_object()
        return self.request.user == heavy.seller
# ============================================
# افزودن/حذف علاقه‌مندی
# ============================================@login_required
def toggle_favorite(request, vehicle_id):
    vehicle_type = request.POST.get('vehicle_type', 'car')
    
    if vehicle_type == 'car':
        vehicle = get_object_or_404(Car, id=vehicle_id)
    elif vehicle_type == 'motorcycle':
        vehicle = get_object_or_404(Motorcycle, id=vehicle_id)
    elif vehicle_type == 'heavy':
        vehicle = get_object_or_404(HeavyVehicle, id=vehicle_id)
    else:
        return JsonResponse({'error': 'نوع نامعتبر'}, status=400)
    
    favorite = Favorite.objects.filter(
        user=request.user,
        vehicle_id=vehicle.id,
        vehicle_type=vehicle_type
    ).first()
    
    if favorite:
        favorite.delete()
        messages.success(request, '❌ از علاقه‌مندی‌ها حذف شد.')
    else:
        Favorite.objects.create(
            user=request.user,
            vehicle_id=vehicle.id,
            vehicle_type=vehicle_type
        )
        messages.success(request, '✅ به علاقه‌مندی‌ها اضافه شد.')
    
    # ✅ redirect بر اساس نوع وسیله نقلیه
    if vehicle_type == 'car':
        return redirect('cars:car_detail', pk=vehicle.pk, slug=vehicle.slug)
    elif vehicle_type == 'motorcycle':
        return redirect('cars:motorcycle_detail', pk=vehicle.pk, slug=vehicle.slug)
    elif vehicle_type == 'heavy':
        return redirect('cars:heavy_detail', pk=vehicle.pk, slug=vehicle.slug)
# ============================================
# API دریافت مدل‌های یک برند
# ============================================
def get_models(request):
    brand_id = request.GET.get('brand_id')
    if brand_id:
        models = CarModel.objects.filter(brand_id=brand_id).order_by('name')
        data = [{'id': m.id, 'name': m.name} for m in models]
        return JsonResponse({'models': data})
    return JsonResponse({'models': []})


# ============================================
# Context Processor
# ============================================
def brands_processor(request):
    """
    Context Processor: فراهم کردن داده‌های مشترک برای همه تمپلیت‌ها
    """
    # ✅ استفاده از car_vehicles به جای car
    brands_with_count = Brand.objects.annotate(
        car_count=Count('car')  # related_name جدید
    ).filter(
        car_count__gt=0
    ).order_by('-car_count')[:10]
    
    return {
        'all_brands': Brand.objects.all().order_by('name')[:20],
        'brands': brands_with_count,  # ← برندهای پرطرفدار با تعداد
        'featured_cars': Car.objects.filter(
            is_active=True,
            is_verified=True,
            is_featured=True
        )[:6] if not request.path.startswith('/admin/') else [],
    }
