# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import UserUpdateForm, ProfileUpdateForm, PhoneRegisterForm
from django.contrib.auth.backends import ModelBackend
from cars.models import Favorite, Car, Motorcycle, HeavyVehicle
from cars.utils import can_post_free_listing, get_listing_price


# ============================================
# CustomLoginView (با پشتیبانی از Draft)
# ============================================

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        # لاگین کاربر
        response = super().form_valid(form)
        
        # ✅ چک کن توکن Draft توی URL یا POST هست
        draft_token = self.request.GET.get('draft') or self.request.POST.get('draft_token')
        
        if draft_token:
            result = _attach_draft_to_user(self.request, self.request.user, draft_token)
            if result:
                return result
        
        messages.success(self.request, '✅ با موفقیت وارد شدید!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['draft_token'] = self.request.GET.get('draft', '')
        return context


# ============================================
# Register (با پشتیبانی از Draft)
# ============================================

def register(request):
    """
    ثبت‌نام کاربر جدید (با پشتیبانی از Draft)
    """
    # ✅ دریافت توکن Draft از URL یا POST
    draft_token = request.GET.get('draft') or request.POST.get('draft_token')
    
    if request.method == 'POST':
        form = PhoneRegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            # ✅ اگه Draft وجود داره، به کاربر متصل کن
            if draft_token:
                result = _attach_draft_to_user(request, user, draft_token)
                if result:
                    return result
            
            messages.success(request, '✅ حساب کاربری شما با موفقیت ایجاد شد!')
            return redirect('cars:car_list')
    else:
        form = PhoneRegisterForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'draft_token': draft_token,
    })


# ============================================
# اتصال Draft به کاربر (با منطق پرداخت)
# ============================================

def _attach_draft_to_user(request, user, draft_token):
    """
    اتصال Draft به کاربر با رعایت منطق پرداخت:
    - آگهی اول رایگان → منتشر
    - آگهی دوم به بعد → نیاز به پرداخت
    
    Returns:
        HttpResponse (redirect) در صورت موفقیت، None در غیر این صورت
    """
    vehicle = None
    vehicle_type = None

    # پیدا کردن Draft در هر سه مدل
    car = Car.objects.filter(draft_token=draft_token, is_draft=True).first()
    if car:
        vehicle, vehicle_type = car, 'car'
    else:
        moto = Motorcycle.objects.filter(draft_token=draft_token, is_draft=True).first()
        if moto:
            vehicle, vehicle_type = moto, 'motorcycle'
        else:
            heavy = HeavyVehicle.objects.filter(draft_token=draft_token, is_draft=True).first()
            if heavy:
                vehicle, vehicle_type = heavy, 'heavy'

    if not vehicle:
        return None

    # اتصال به کاربر
    vehicle.seller = user
    vehicle.is_draft = False
    vehicle.draft_token = None

    # ✅ منطق پرداخت
    if can_post_free_listing(user):
        # آگهی رایگان
        vehicle.is_active = True
        vehicle.is_verified = False
        vehicle.is_paid = False
        vehicle.save()

        request.session.pop('draft_token', None)
        request.session.pop('draft_type', None)

        messages.success(request, '🎉 آگهی شما با موفقیت ثبت شد!')

        if vehicle_type == 'car':
            return redirect('cars:car_detail', pk=vehicle.pk, slug=vehicle.slug)
        elif vehicle_type == 'motorcycle':
            return redirect('cars:motorcycle_detail', pk=vehicle.pk, slug=vehicle.slug)
        else:
            return redirect('cars:heavy_detail', pk=vehicle.pk, slug=vehicle.slug)

    else:
        # نیاز به پرداخت
        price = get_listing_price(user)
        vehicle.is_active = False
        vehicle.is_verified = False
        vehicle.is_paid = False
        vehicle.payment_amount = price
        vehicle.save()

        request.session.pop('draft_token', None)
        request.session.pop('draft_type', None)

        messages.info(
            request,
            '💳 برای انتشار آگهی، لطفاً پرداخت را تکمیل کنید.'
        )

        return redirect(
            'payments:start_payment',
            vehicle_type=vehicle_type,
            vehicle_id=vehicle.id
        )


# ============================================
# Profile
# ============================================

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
        'total_motorcycles': Motorcycle.objects.filter(seller=request.user).count(),
        'total_heavies': HeavyVehicle.objects.filter(seller=request.user).count(),
    }
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'stats': stats,
    }
    return render(request, 'accounts/profile.html', context)


# ============================================
# My Cars
# ============================================

@login_required
def my_car(request):
    filter_type = request.GET.get('filter', 'all')
    
    cars = Car.objects.filter(seller=request.user)
    
    if filter_type == 'active':
        cars = cars.filter(is_active=True, is_verified=True)
    elif filter_type == 'sold':
        cars = cars.filter(is_sold=True)
    elif filter_type == 'inactive':
        cars = cars.filter(is_active=False)
    elif filter_type == 'pending':
        cars = cars.filter(is_active=True, is_verified=False)
    
    cars = cars.order_by('-created_at')
    
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


# ============================================
# Favorites
# ============================================

@login_required
def favorites(request):
    user_favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    
    favorite_cars = []
    favorite_motorcycles = []
    favorite_heavies = []
    
    for fav in user_favorites:
        if fav.vehicle_type == 'car':
            car = Car.objects.filter(id=fav.vehicle_id).prefetch_related('car_images').first()
            if car:
                favorite_cars.append(car)
        elif fav.vehicle_type == 'motorcycle':
            moto = Motorcycle.objects.filter(id=fav.vehicle_id).prefetch_related('motorcycle_images').first()
            if moto:
                favorite_motorcycles.append(moto)
        elif fav.vehicle_type == 'heavy':
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


# ============================================
# CSRF Failure
# ============================================

def csrf_failure(request, reason=""):
    """صفحه خطای CSRF سفارشی"""
    return render(request, 'accounts/csrf_failure.html', status=403)