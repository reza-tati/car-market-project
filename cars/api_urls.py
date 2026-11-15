# cars/api_urls.py (ایجاد فایل جدید)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import BrandViewSet, CarModelViewSet, CarViewSet, CarImageViewSet
from . import views
import json
from django.http import JsonResponse
from django.views import View
from cars.models import VehicleCatalogModel

from cars.services.price_estimator import (
    estimate_motorcycle_price,
    estimate_heavy_vehicle_price,
)
from cars.models import VehicleCatalogModel
router = DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'models', CarModelViewSet)
router.register(r'cars', CarViewSet)
router.register(r'car-images', CarImageViewSet)
class VehiclePriceEstimateView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body or "{}")
            vehicle_type = data.get("vehicle_type")

            if vehicle_type == "motorcycle":
                try:
                    catalog_model_id = int(data["catalog_model_id"])
                    catalog_model = VehicleCatalogModel.objects.get(
                        pk=catalog_model_id,
                        vehicle_type="motorcycle",
                        is_active=True,
                    )
                except (KeyError, TypeError, ValueError):
                    return JsonResponse(
                        {"error": "شناسهٔ مدل معتبر نیست."},
                        status=400,
                    )
                except VehicleCatalogModel.DoesNotExist:
                    return JsonResponse(
                        {"error": "مدل موتورسیکلت پیدا نشد."},
                        status=404,
                    )

 

                result = estimate_motorcycle_price(
                    brand_id=catalog_model.brand_id,
                    model_name=str(catalog_model),
                    year=int(data["year"]) if data.get("year") else None,
                    city=data.get("city") or None,
                    mileage=int(data["mileage"]) if data.get("mileage") else None,
                    engine_cc=int(data["engine_cc"]) if data.get("engine_cc") else None,
                )

            elif vehicle_type == "heavy":
                result = estimate_heavy_vehicle_price(
                    catalog_model_id=int(data.get("catalog_model_id")),
                    year=int(data["year"]) if data.get("year") else None,
                    city=data.get("city") or None,
                    heavy_type=data.get("heavy_type") or None,
                    load_capacity=(
                        float(data["load_capacity"])
                        if data.get("load_capacity")
                        else None
                    ),
                )

            else:
                return JsonResponse(
                    {"error": "نوع وسیله معتبر نیست."},
                    status=400,
                )

            if result is None:
                return JsonResponse({
                    "available": False,
                    "message": "آگهی مشابهی برای برآورد پیدا نشد.",
                })

            return JsonResponse({"available": True, **result})

        except (TypeError, ValueError, json.JSONDecodeError):
            return JsonResponse(
                {"error": "اطلاعات ارسالی معتبر نیست."},
                status=400,
            )

urlpatterns = [
    path("get-models/", views.get_models, name="get_models"),
    path("catalog/brands/", views.catalog_brands, name="catalog_brands"),
    path("catalog/models/", views.catalog_models, name="catalog_models"),
    path("catalog/variants/", views.catalog_variants, name="catalog_variants"),
    path("", include(router.urls)),
    path(
        "estimate-vehicle-price/",
        VehiclePriceEstimateView.as_view(),
        name="estimate_vehicle_price",
    ),
]
