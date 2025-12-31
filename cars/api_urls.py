# cars/api_urls.py (ایجاد فایل جدید)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import BrandViewSet, CarModelViewSet, CarViewSet, CarImageViewSet

router = DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'models', CarModelViewSet)
router.register(r'cars', CarViewSet)
router.register(r'car-images', CarImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]