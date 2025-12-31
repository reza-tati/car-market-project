from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from cars.models import Car

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        messages.success(self.request,'با موفقیت وارد شدید!')
        return super().form_valid(form)
    
def register(request):
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'حساب کاربری شما با موفقیت ایجاد شد!') 
                return redirect('cars:car_list')
        else:
            form = UserRegisterForm()
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
            context = {
                'u_form': u_form,
                'p_form': p_form,
            }
            return render(request, 'accounts/profile.html', context)
        
@login_required
def my_car(request):
        cars = Car.objects.filter(seller=request.user).order_by('created_at')
        return render(request,'accounts/my_cars.html',{'cars':cars})
        
@login_required
def favorites(request):
        favorite_cars = Car.objects.filter(favorited_by__user=request.user)
        return render(request, 'accounts/favorites.html', {'favorite_cars':favorite_cars})
    


# Create your views here.
