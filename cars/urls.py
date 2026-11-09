# cars/urls.py
app_name = 'cars'
from django.urls import path
from . import views
from .views import CarPriceEstimateView
from .api_urls import VehiclePriceEstimateView


app_name = 'cars'

urlpatterns = [
    # ===== لیست‌ها =====
    path('', views.CarListView.as_view(), name='car_list'),
    path('motorcycles/', views.MotorcycleListView.as_view(), name='motorcycle_list'),
    path('heavy-vehicles/', views.HeavyVehicleListView.as_view(), name='heavy_list'),
    path("estimate-car-price/", CarPriceEstimateView.as_view(), name="estimate_car_price"),

    # ===== ✅ ایجاد (قبل از car_detail) =====
    path('car/new/', views.CarCreateView.as_view(), name='car_create'),
    path('motorcycle/new/', views.MotorcycleCreateView.as_view(), name='motorcycle_create'),
    path('heavy-vehicle/new/', views.HeavyVehicleCreateView.as_view(), name='heavy_create'),
    
    # ===== ✅ ویرایش و حذف (قبل از car_detail) =====
    path('car/<int:pk>/edit/', views.CarUpdateView.as_view(), name='car_update'),
    path('car/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
    path('motorcycle/<int:pk>/edit/', views.MotorcycleUpdateView.as_view(), name='motorcycle_update'),
    path('motorcycle/<int:pk>/delete/', views.MotorcycleDeleteView.as_view(), name='motorcycle_delete'),
    
    # ===== ویرایش و حذف ماشین سنگین =====
    path('heavy-vehicle/<int:pk>/edit/', views.HeavyVehicleUpdateView.as_view(), name='heavy_update'),
    path('heavy-vehicle/<int:pk>/delete/', views.HeavyVehicleDeleteView.as_view(), name='heavy_delete'),
    # ===== ✅ علاقه‌مندی (قبل از car_detail) =====
    path('favorite/<int:vehicle_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # ===== جزئیات (باید در آخر باشه چون slug هرچیزی رو قبول میکنه) =====
    path('car/<int:pk>/<slug:slug>/', views.CarDetailView.as_view(), name='car_detail'),
    path('motorcycle/<int:pk>/<slug:slug>/', views.MotorcycleDetailView.as_view(), name='motorcycle_detail'),
    path('heavy-vehicle/<int:pk>/<slug:slug>/', views.HeavyVehicleDetailView.as_view(), name='heavy_detail'),
    path(
    "estimate-vehicle-price/",
    VehiclePriceEstimateView.as_view(),
    name="estimate_vehicle_price",
),
path(
    "ads/<str:vehicle_type>/<int:pk>/mark-sold/",
    views.mark_vehicle_sold,
    name="mark_vehicle_sold",
),





    
]