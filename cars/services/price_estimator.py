from statistics import median, quantiles
from django.db.models import Q
from cars.models import Motorcycle, HeavyVehicle, Car

def estimate_car_price(
    *,
    catalog_model_id,
    year,
    mileage=None,
    engine_cc=None,
    transmission=None,
    condition=None,
    city=None,
):
    if not catalog_model_id or not year:
        return None

    base_qs = (
        Car.objects.filter(
            catalog_model_id=catalog_model_id,
            is_active=True,
            is_verified=True,
            is_sold=False,
            is_draft=False,
        )
        .exclude(price__lte=0)
        .only(
            "price",
            "year",
            "mileage",
            "engine_capacity",
            "transmission",
            "condition",
            "city",
        )
    )

    candidates = list(
        base_qs.filter(year__range=(year - 2, year + 2))[:500]
    )

    if len(candidates) < 3:
        candidates = list(
            base_qs.filter(year__range=(year - 5, year + 5))[:500]
        )

    def similarity_score(car):
        score = abs(car.year - year)

        if mileage is not None and car.mileage is not None:
            score += abs(car.mileage - mileage) / 50_000

        if engine_cc is not None and car.engine_capacity is not None:
            score += abs(car.engine_capacity - engine_cc) / 1_000

        if transmission and car.transmission != transmission:
            score += 1

        if condition and car.condition != condition:
            score += 1

        if city and car.city != city:
            score += 0.5

        return score

    candidates.sort(key=similarity_score)
    selected = candidates[:20]

    if len(selected) < 3:
        return {
            "low": None,
            "median": None,
            "high": None,
            "sample_size": len(selected),
        }

    prices = sorted(int(car.price) for car in selected)
    low, _, high = quantiles(prices, n=4, method="inclusive")

    return {
        "low": round(low),
        "median": round(median(prices)),
        "high": round(high),
        "sample_size": len(prices),
    }



def _price_range(candidates):
    prices = sorted(
        int(price)
        for price in candidates.values_list("price", flat=True)
        if price and int(price) > 0
    )

    if not prices:
        return None

    # چارک‌ها به روش ساده و بدون وابستگی اضافه
    def percentile(values, fraction):
        index = round((len(values) - 1) * fraction)
        return values[index]

    return {
        "low": percentile(prices, 0.25),
        "median": int(median(prices)),
        "high": percentile(prices, 0.75),
        "sample_size": len(prices),
    }


def _base_candidates(model, brand_id, model_name, year, city):
    candidates = model.objects.filter(
        is_active=True,
        is_draft=False,
        price__gt=0,
        brand_id=brand_id,
        model_name__iexact=model_name,
    )

    if year:
        candidates = candidates.filter(year__range=(year - 2, year + 2))

    if city:
        city_candidates = candidates.filter(city=city)
        # اگر شهر آگهی کافی ندارد، از آگهی‌های شهرهای دیگر هم استفاده کن.
        if city_candidates.count() >= 3:
            candidates = city_candidates

    if candidates.count() < 3 and year:
        candidates = model.objects.filter(
            is_active=True,
            is_draft=False,
            price__gt=0,
            brand_id=brand_id,
            model_name__iexact=model_name,
            year__range=(year - 5, year + 5),
        )
        if city and candidates.filter(city=city).count() >= 3:
            candidates = candidates.filter(city=city)

    return candidates


def estimate_motorcycle_price(
    *, brand_id, model_name, year=None, city=None, mileage=None, engine_cc=None
):
    candidates = _base_candidates(
        Motorcycle, brand_id, model_name, year, city
    )

    # مشخصات اختیاری‌اند؛ فقط وقتی داده کافی باشد، فیلترشان کن.
    if engine_cc:
        similar_engine = candidates.filter(engine_cc=engine_cc)
        if similar_engine.count() >= 3:
            candidates = similar_engine

    if mileage is not None:
        similar_mileage = candidates.filter(
            mileage__gte=max(0, mileage - 20000),
            mileage__lte=mileage + 20000,
        )
        if similar_mileage.count() >= 3:
            candidates = similar_mileage

    return _price_range(candidates)


def estimate_heavy_vehicle_price(
    *,
    catalog_model_id,
    year=None,
    city=None,
    heavy_type=None,
    load_capacity=None,
):
    if not catalog_model_id:
        return None

    base_candidates = HeavyVehicle.objects.filter(
        catalog_model_id=catalog_model_id,
        is_active=True,
        is_draft=False,
        price__gt=0,
    )

    candidates = base_candidates

    if year:
        year = int(year)
        candidates = base_candidates.filter(
            year__range=(year - 2, year + 2)
        )

        if candidates.count() < 3:
            candidates = base_candidates.filter(
                year__range=(year - 5, year + 5)
            )

    if city:
        city_candidates = candidates.filter(city=city)
        if city_candidates.count() >= 3:
            candidates = city_candidates

    if heavy_type:
        type_candidates = candidates.filter(heavy_type=heavy_type)
        if type_candidates.count() >= 3:
            candidates = type_candidates

    if load_capacity:
        capacity = float(load_capacity)
        capacity_candidates = candidates.filter(
            load_capacity__gte=capacity * 0.8,
            load_capacity__lte=capacity * 1.2,
        )
        if capacity_candidates.count() >= 3:
            candidates = capacity_candidates

    return _price_range(candidates)
