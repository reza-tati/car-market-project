# cars/urls.py
from django.urls import path
from . import views

app_name = 'cars'  # namespace

urlpatterns = [
    # صفحه اصلی - لیست خودروها
    path('', views.CarListView.as_view(), name='car_list'),

     # ویرایش خودرو
    path('car/<int:pk>/edit/', views.CarUpdateView.as_view(), name='car_update'),

    # حذف خودرو
    path('car/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),

     path('car/<int:car_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    # جزئیات خودرو (با slug برای SEO)
    path('car/<int:pk>/<slug:slug>/', views.CarDetailView.as_view(), name='car_detail'),
    
    # ایجاد خودرو جدید
    path('car/new/', views.CarCreateView.as_view(), name='car_create'),
   
    # افزودن/حذف علاقه‌مندی (AJAX)
   
    

    # API دریافت مدل‌ها (AJAX)
    path('api/get-models/', views.get_models, name='get_models'),
]
