from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
app_name = 'accounts'
urlpatterns = [
    # ثبت‌نام
    path('register/', views.register, name='register'),
    
    # ورود (با ویوی سفارشی)
    path('login/', views.CustomLoginView.as_view(), name='login'),
    
    # خروج
    path('logout/', 
         auth_views.LogoutView.as_view(template_name='accounts/logout.html'), 
         name='logout'),
    
    # پروفایل
    path('profile/', views.profile, name='profile'),
    
    # خودروهای من
    path('my-cars/', views.my_car, name='my_cars'),
    
    # علاقه‌مندی‌ها
    path('favorites/', views.favorites, name='favorites'),
    
    # تغییر رمز عبور
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/password_change.html',
             success_url='/accounts/password-change/done/'
         ), 
         name='password_change'),
    
    # تأیید تغییر رمز عبور
    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ), 
         name='password_change_done'),
]
