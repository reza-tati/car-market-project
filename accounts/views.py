from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import UserUpdateForm, ProfileUpdateForm, PhoneRegisterForm
from django.contrib.auth.backends import ModelBackend
from cars.models import Favorite, Car, Motorcycle, HeavyVehicle



class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        messages.success(self.request,'با موفقیت وارد شدید!')
        return super().form_valid(form)
    
def register(request):
        if request.method == 'POST':
            form = PhoneRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, 'حساب کاربری شما با موفقیت ایجاد شد!') 
                return redirect('cars:car_list')
        else:
            form = PhoneRegisterForm()
        return render(request, 'accounts/register.html',{'form':form})
    
@login_required
def profile(request):
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(
                request.POST,
                request.FILES,
                instance=request.user.profile
            )
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'پروفایل شما با موفقیت به روز رسانی شد!')
                return redirect('accounts:profile')
        else:
                u_form = UserUpdateForm(instance=request.user)
                p_form = ProfileUpdateForm(instance=request.user.profile)
        
        stats = {
        'total_cars': Car.objects.filter(seller=request.user).count(),
        'active_cars': Car.objects.filter(seller=request.user, is_active=True, is_verified=True).count(),
        'sold_cars': Car.objects.filter(seller=request.user, is_sold=True).count(),
        'favorite_count': Favorite.objects.filter(user=request.user).count(),
        
        # اگه موتور و سنگین هم میخوای:
        'total_motorcycles': Motorcycle.objects.filter(seller=request.user).count(),
        'total_heavies': HeavyVehicle.objects.filter(seller=request.user).count(),
    }
        
        context = {
            'u_form': u_form,
            'p_form': p_form,
            'stats':stats,
        }
        return render(request, 'accounts/profile.html', context)
        
@login_required
def my_car(request):
    # دریافت پارامتر فیلتر از URL (مثلاً ?filter=active)
    filter_type = request.GET.get('filter', 'all')
    
    # دریافت خودروهای کاربر
    cars = Car.objects.filter(seller=request.user)
    
    # اعمال فیلتر
    if filter_type == 'active':
        cars = cars.filter(is_active=True, is_verified=True)
    elif filter_type == 'sold':
        cars = cars.filter(is_sold=True)
    elif filter_type == 'inactive':
        cars = cars.filter(is_active=False)
    elif filter_type == 'pending':
        cars = cars.filter(is_active=True, is_verified=False)
    
    # مرتب‌سازی (جدیدترین اول)
    cars = cars.order_by('-created_at')
    
    # محاسبه آمار
    stats = {
        'total': Car.objects.filter(seller=request.user).count(),
        'active': Car.objects.filter(seller=request.user, is_active=True, is_verified=True).count(),
        'sold': Car.objects.filter(seller=request.user, is_sold=True).count(),
        'with_views': Car.objects.filter(seller=request.user, views__gt=0).count(),
        'pending': Car.objects.filter(seller=request.user, is_active=True, is_verified=False).count(),
    }
    
    context = {
        'cars': cars,
        'stats': stats,
        'current_filter': filter_type,
    }
    
    return render(request, 'accounts/my_cars.html', context)  


@login_required
def favorites(request):
    user_favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    
    favorite_cars = []
    favorite_motorcycles = []
    favorite_heavies = []
    
    for fav in user_favorites:
        if fav.vehicle_type == 'car':
            # ✅ prefetch_related برای car_images
            car = Car.objects.filter(id=fav.vehicle_id).prefetch_related('car_images').first()
            if car:
                favorite_cars.append(car)
        elif fav.vehicle_type == 'motorcycle':
            # ✅ prefetch_related برای motorcycle_images
            moto = Motorcycle.objects.filter(id=fav.vehicle_id).prefetch_related('motorcycle_images').first()
            if moto:
                favorite_motorcycles.append(moto)
        elif fav.vehicle_type == 'heavy':
            # ✅ prefetch_related برای heavy_images
            heavy = HeavyVehicle.objects.filter(id=fav.vehicle_id).prefetch_related('heavy_images').first()
            if heavy:
                favorite_heavies.append(heavy)
    
    context = {
        'favorite_cars': favorite_cars,
        'favorite_motorcycles': favorite_motorcycles,
        'favorite_heavies': favorite_heavies,
        'total_favorites': user_favorites.count(),
    }
    
    return render(request, 'accounts/favorites.html', context)

from django.shortcuts import render

def csrf_failure(request, reason=""):
    """صفحه خطای CSRF سفارشی"""
    return render(request, 'accounts/csrf_failure.html', status=403)