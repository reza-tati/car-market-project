# cars/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from itertools import chain
import uuid
from django.views import View
from django.utils import timezone
from django.urls import reverse
from cars.utils import can_post_free_listing, get_listing_price
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
            cars = Car.objects.filter(
                is_active=True, 
                is_verified=True,
                is_draft=False  # ← Draftها رو نشون نده
            ).select_related('brand', 'model', 'seller').prefetch_related('car_images')
            all_vehicles = list(cars)
            
        elif vehicle_type == 'motorcycle':
            # فقط موتورسیکلت
            motorcycles = Motorcycle.objects.filter(
                is_active=True, 
                is_verified=True,
                is_draft=False  # ← Draftها رو نشون نده
            ).select_related('seller').prefetch_related('motorcycle_images')
            all_vehicles = list(motorcycles)
            
        elif vehicle_type == 'heavy':
            # فقط ماشین سنگین
            heavies = HeavyVehicle.objects.filter(
                is_active=True, 
                is_verified=True,
                is_draft=False  # ← Draftها رو نشون نده
            ).select_related('seller').prefetch_related('heavy_images')
            all_vehicles = list(heavies)
            
        else:
            # همه وسایل نقلیه (پیش‌فرض)
            cars = Car.objects.filter(
                is_active=True, 
                is_verified=True,
                is_draft=False  # ← Draftها رو نشون نده
            ).select_related('brand', 'model', 'seller').prefetch_related('car_images')
            
            motorcycles = Motorcycle.objects.filter(
                is_active=True, 
                is_verified=True,
                is_draft=False  # ← Draftها رو نشون نده
            ).select_related('seller').prefetch_related('motorcycle_images')
            
            heavies = HeavyVehicle.objects.filter(
                is_active=True, 
                is_verified=True,
                is_draft=False  # ← Draftها رو نشون نده
            ).select_related('seller').prefetch_related('heavy_images')
            
            all_vehicles = sorted(
                chain(cars, motorcycles, heavies),
                key=lambda x: x.created_at,
                reverse=True
            )
        
        # ===== ۳. اعمال فیلترها =====
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
        paginator = Paginator(all_vehicles, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        self.page_obj = page_obj
        
        return page_obj.object_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # اضافه کردن page_obj برای صفحه‌بندی
        if hasattr(self, 'page_obj'):
            context['page_obj'] = self.page_obj
            context['is_paginated'] = self.page_obj.has_other_pages()
        
        # favorite_ids
        if self.request.user.is_authenticated:
            context['favorite_ids'] = list(Favorite.objects.filter(
                user=self.request.user
            ).values_list('vehicle_id', flat=True))
        else:
            context['favorite_ids'] = []
        
        # برندها
        context['brands'] = Brand.objects.annotate(
            car_count=Count('car')
        ).filter(car_count__gt=0).order_by('-car_count')[:10]
        
        context['total_cars'] = Car.objects.filter(
            is_active=True, 
            is_verified=True,
            is_draft=False
        ).count()
        
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
            is_verified=True,
            is_draft=False  # ← Draftها رو نشون نده
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
            is_verified=True,
            is_draft=False  # ← Draftها رو نشون نده
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
        return Car.objects.filter(
            is_draft=False  # ← Draftها رو نشون نده
        ).select_related(
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
        # ✅ Draftها رو نشون نده
        return Motorcycle.objects.filter(
            is_draft=False
        ).select_related('seller__profile').prefetch_related('motorcycle_images')
    
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
        # ✅ Draftها رو نشون نده
        return HeavyVehicle.objects.filter(
            is_draft=False
        ).select_related('seller__profile').prefetch_related('heavy_images')

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
class CarCreateView(View):
    """
    ثبت آگهی خودرو - کاربر مهمان می‌تونه اطلاعات رو پر کنه
    """
    
    def get(self, request):
        """نمایش فرم خالی"""
        form = CarForm()
        formset = CarImageFormSet()
        
        # ✅ اطلاعات آگهی رایگان
        from cars.utils import can_post_free_listing, get_listing_price
        
        context = {
            'form': form,
            'formset': formset,
            'can_post_free': can_post_free_listing(request.user) if request.user.is_authenticated else False,
            'listing_price': get_listing_price(request.user) if request.user.is_authenticated else 0,
        }
        
        return render(request, 'cars/car_form.html', context)
    def post(self, request):
        """پردازش فرم"""
        form = CarForm(request.POST, request.FILES)
        formset = CarImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            # ✅ چک کن کاربر لاگین کرده یا نه
            if not request.user.is_authenticated:
                # کاربر مهمان: Draft ذخیره کن
                return self._save_draft(request, form, formset)
            
            # کاربر لاگین: مستقیم ذخیره کن
            return self._save_car(request, form, formset)
        
        # اگه فرم معتبر نبود
        messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
        return render(request, 'cars/car_form.html', {
            'form': form,
            'formset': formset,
        })
    
    def _save_draft(self, request, form, formset):
        """ذخیره آگهی به عنوان Draft"""
        # ساخت توکن یکتا
        draft_token = str(uuid.uuid4())
        
        # ذخیره خودرو به عنوان Draft
        car = form.save(commit=False)
        car.seller = None              # ← فروشنده نداره
        car.is_draft = True            # ← پیش‌نویس
        car.is_active = False          # ← توی لیست نمایش داده نشه
        car.is_verified = False        # ← نیاز به تایید
        car.draft_token = draft_token  # ← توکن یکتا
        car.vehicle_type = 'car'
        car.save()
        
        # ذخیره تصاویر
        formset.instance = car
        formset.save()
        
        # ✅ ذخیره توکن توی Session
        request.session['draft_token'] = draft_token
        request.session['draft_type'] = 'car'
        
        messages.success(
            request,
            '✅ اطلاعات آگهی شما ذخیره شد! برای ثبت نهایی، لطفاً ثبت‌نام کنید.'
        )
        
        # هدایت به صفحه ثبت‌نام با توکن
        return redirect(f"{reverse('accounts:register')}?draft={draft_token}")
    
    def _save_car(self, request, form, formset):
        """ذخیره نهایی خودرو (کاربر لاگین شده)"""
        from cars.utils import can_post_free_listing, get_listing_price
        
        car = form.save(commit=False)
        car.seller = request.user
        car.vehicle_type = 'car'
        car.is_draft = False
        
        # ✅ چک کن آگهی رایگان هست یا نیاز به پرداخت داره
        if can_post_free_listing(request.user):
            # آگهی رایگان
            car.is_active = True
            car.is_verified = False
            car.is_paid = False
            car.save()
            
            formset.instance = car
            formset.save()
            
            messages.success(request, '🎉 آگهی شما رایگان ثبت شد! پس از تایید نمایش داده می‌شود.')
            return redirect('cars:car_detail', pk=car.pk, slug=car.slug)
        
        else:
            # آگهی نیاز به پرداخت داره
            price = get_listing_price(request.user)
            
            car.is_active = False
            car.is_verified = False
            car.is_paid = False
            car.payment_amount = price
            car.save()
            
            formset.instance = car
            formset.save()
            return redirect('payments:start_payment', vehicle_type='car', vehicle_id=car.id)  # ← این خط درسته
# ============================================
# ایجاد موتورسیکلت
# ============================================

class MotorcycleCreateView(View):
    """
    ثبت آگهی موتورسیکلت - کاربر مهمان می‌تونه اطلاعات رو پر کنه
    """
    
    def get(self, request):
        form = MotorcycleForm()
        formset = MotorcycleImageFormSet()
        
        # ✅ اطلاعات آگهی رایگان
        from cars.utils import can_post_free_listing, get_listing_price
        
        context = {
            'form': form,
            'formset': formset,
            'can_post_free': can_post_free_listing(request.user) if request.user.is_authenticated else False,
            'listing_price': get_listing_price(request.user) if request.user.is_authenticated else 0,
        }
        
        return render(request, 'cars/motorcycle_form.html', context)
    def post(self, request):
        form = MotorcycleForm(request.POST, request.FILES)
        formset = MotorcycleImageFormSet(request.POST, request.FILES)
        if not form.is_valid():
            print("=" * 60)
            print("❌ Motorcycle Form Errors:")
            print(form.errors)
            print("=" * 60)

        if not formset.is_valid():
            print("=" * 60)
            print("❌ Motorcycle Formset Errors:")
            print(formset.errors)
            print(formset.non_form_errors())
            print("=" * 60)
        if form.is_valid() and formset.is_valid():
            # ✅ چک کن کاربر لاگین کرده یا نه
            if not request.user.is_authenticated:
                return self._save_draft(request, form, formset)
            
            return self._save_motorcycle(request, form, formset)
        
        messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
        return render(request, 'cars/motorcycle_form.html', {
            'form': form,
            'formset': formset,
        })
    
    def _save_draft(self, request, form, formset):
        """ذخیره آگهی به عنوان Draft"""
        draft_token = str(uuid.uuid4())
        
        motorcycle = form.save(commit=False)
        motorcycle.seller = None
        motorcycle.is_draft = True
        motorcycle.is_active = False
        motorcycle.is_verified = False
        motorcycle.draft_token = draft_token
        motorcycle.vehicle_type = 'motorcycle'
        motorcycle.save()
        
        formset.instance = motorcycle
        formset.save()
        
        request.session['draft_token'] = draft_token
        request.session['draft_type'] = 'motorcycle'
        
        messages.success(
            request,
            '✅ اطلاعات آگهی شما ذخیره شد! برای ثبت نهایی، لطفاً ثبت‌نام کنید.'
        )
        
        return redirect(f"{reverse('accounts:register')}?draft={draft_token}")
    
    def _save_motorcycle(self, request, form, formset):
        """ذخیره نهایی موتورسیکلت"""
        from cars.utils import can_post_free_listing, get_listing_price
        
        motorcycle = form.save(commit=False)
        motorcycle.seller = request.user
        motorcycle.vehicle_type = 'motorcycle'
        motorcycle.is_draft = False
        
        if can_post_free_listing(request.user):
            motorcycle.is_active = True
            motorcycle.is_verified = False
            motorcycle.is_paid = False
            motorcycle.save()
            
            formset.instance = motorcycle
            formset.save()
            
            messages.success(request, '🎉 موتورسیکلت شما رایگان ثبت شد! پس از تایید نمایش داده می‌شود.')
            return redirect('cars:motorcycle_detail', pk=motorcycle.pk, slug=motorcycle.slug)
        
        else:
            price = get_listing_price(request.user)
            
            motorcycle.is_active = False
            motorcycle.is_verified = False
            motorcycle.is_paid = False
            motorcycle.payment_amount = price
            motorcycle.save()
            
            formset.instance = motorcycle
            formset.save()
            return redirect('payments:start_payment', vehicle_type='motorcycle', vehicle_id=motorcycle.id)  # ← این خط درسته
# ============================================
# ایجاد ماشین سنگین
# ============================================
class HeavyVehicleCreateView(View):
    """
    ثبت آگهی ماشین سنگین - کاربر مهمان می‌تونه اطلاعات رو پر کنه
    """
    
    def get(self, request):
        form = HeavyVehicleForm()
        formset = HeavyVehicleImageFormSet()
        
        # ✅ اطلاعات آگهی رایگان
        from cars.utils import can_post_free_listing, get_listing_price
        
        context = {
            'form': form,
            'formset': formset,
            'can_post_free': can_post_free_listing(request.user) if request.user.is_authenticated else False,
            'listing_price': get_listing_price(request.user) if request.user.is_authenticated else 0,
        }
        
        return render(request, 'cars/heavy_form.html', context)

    def post(self, request):
        form = HeavyVehicleForm(request.POST, request.FILES)
        formset = HeavyVehicleImageFormSet(request.POST, request.FILES)

        if not form.is_valid():
            print("=" * 60)
            print("❌ HeavyVehicle Form Errors:")
            print(form.errors)
            print("=" * 60)

        if not formset.is_valid():
            print("=" * 60)
            print("❌ HeavyVehicle Formset Errors:")
            print(formset.errors)
            print(formset.non_form_errors())
            print("=" * 60)
        
        if form.is_valid() and formset.is_valid():
            # ✅ چک کن کاربر لاگین کرده یا نه
            if not request.user.is_authenticated:
                return self._save_draft(request, form, formset)
            
            return self._save_heavy(request, form, formset)
        
        messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
        return render(request, 'cars/heavy_form.html', {
            'form': form,
            'formset': formset,
        })
    
    def _save_draft(self, request, form, formset):
        """ذخیره آگهی به عنوان Draft"""
        draft_token = str(uuid.uuid4())
        heavy = form.save(commit=False)
        heavy.seller = None
        heavy.is_draft = True
        heavy.is_active = False
        heavy.is_verified = False
        heavy.draft_token = draft_token
        heavy.vehicle_type = 'heavy'
        heavy.save()
        formset.instance = heavy
        formset.save()
        request.session['draft_token'] = draft_token
        request.session['draft_type'] = 'heavy'
        messages.success(
            request,
            '✅ اطلاعات آگهی شما ذخیره شد! برای ثبت نهایی، لطفاً ثبت‌نام کنید.'
        )
        return redirect(f"{reverse('accounts:register')}?draft={draft_token}")
    
    def _save_heavy(self, request, form, formset):
        """ذخیره نهایی ماشین سنگین"""
        from cars.utils import can_post_free_listing, get_listing_price
        
        heavy = form.save(commit=False)
        heavy.seller = request.user
        heavy.vehicle_type = 'heavy'
        heavy.is_draft = False
        
        if can_post_free_listing(request.user):
            heavy.is_active = True
            heavy.is_verified = False
            heavy.is_paid = False
            heavy.save()
            formset.instance = heavy
            formset.save()
            messages.success(request, '🎉 ماشین سنگین شما رایگان ثبت شد! پس از تایید نمایش داده می‌شود.')
            return redirect('cars:heavy_detail', pk=heavy.pk, slug=heavy.slug)
        
        else:
            price = get_listing_price(request.user)
            heavy.is_active = False
            heavy.is_verified = False
            heavy.is_paid = False
            heavy.payment_amount = price
            heavy.save()
            formset.instance = heavy
            formset.save()
            return redirect('payments:start_payment', vehicle_type='heavy', vehicle_id=heavy.id)
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
# ============================================
# ============================================
# ❤️ علاقه‌مندی‌ها (قلب) — AJAX + سازگار با فرم‌های قدیمی
# ============================================
VEHICLE_MODELS = {
    'car': Car,
    'motorcycle': Motorcycle,
    'heavy': HeavyVehicle,
}

def toggle_favorite(request, vehicle_id):
    """کلیک روی قلب: افزودن/حذف علاقه‌مندی"""
    vehicle_type = (
        request.GET.get('type')
        or request.POST.get('type')
        or request.POST.get('vehicle_type')   # ← سازگار با فرم صفحات جزئیات
    )
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # اگه نوع نفرستاده شده، خودمون کشفش می‌کنیم
    if vehicle_type not in VEHICLE_MODELS:
        vehicle_type = None
        for vtype, vmodel in VEHICLE_MODELS.items():
            if vmodel.objects.filter(pk=vehicle_id).exists():
                vehicle_type = vtype
                break
        if vehicle_type is None:
            if is_ajax:
                return JsonResponse({'error': 'not_found'}, status=404)
            return redirect('home')

    Model = VEHICLE_MODELS[vehicle_type]
    vehicle = get_object_or_404(Model, pk=vehicle_id)

    # 👤 کاربر مهمان → هدایت به ورود
    if not request.user.is_authenticated:
        login_url = reverse('accounts:login')
        if is_ajax:
            return JsonResponse({'login_required': True, 'login_url': login_url})
        next_url = request.META.get('HTTP_REFERER') or vehicle.get_absolute_url()
        return redirect(f'{login_url}?next={next_url}')

    # ❤️ Toggle: اگه هست حذف، اگه نیست اضافه
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        vehicle_id=vehicle.id,
        vehicle_type=vehicle_type,
    )
    if created:
        favorited = True
    else:
        favorite.delete()
        favorited = False

    if is_ajax:
        return JsonResponse({'favorited': favorited})
    return redirect(request.META.get('HTTP_REFERER') or vehicle.get_absolute_url())
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


from django.views.generic import ListView

class HomeView(ListView):
    model = Car
    template_name = 'index.html'
    context_object_name = 'latest_cars'
    
    def get_queryset(self):
        return Car.objects.filter(is_active=True, is_verified=True, is_draft=False).order_by('-created_at')[:4]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_heavies'] = HeavyVehicle.objects.filter(is_active=True, is_verified=True, is_draft=False).order_by('-created_at')[:4]
        context['latest_motorcycles'] = Motorcycle.objects.filter(is_active=True, is_verified=True, is_draft=False).order_by('-created_at')[:4]
        return context