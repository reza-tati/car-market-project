from statistics import median, quantiles
from django.db.models import Q
from cars.models import Motorcycle, HeavyVehicle, Car

def estimate_car_price(
    *,
    catalog_model_id,
    year,
    mileage,
    transmission=None,
    condition=None,
    city=None,
):
    if not catalog_model_id or not year or mileage is None:
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
        .only("price", "year", "mileage", "transmission", "condition", "city")
    )

    year_tolerance = 2
    candidates = list(
        base_qs.filter(
            year__range=(year - year_tolerance, year + year_tolerance)
        )[:500]
    )

    if len(candidates) < 3:
        year_tolerance = 5
        candidates = list(
            base_qs.filter(
                year__range=(year - year_tolerance, year + year_tolerance)
            )[:500]
        )


    def similarity_score(car):
        score = abs(car.year - year) + abs(car.mileage - mileage) / 50_000

        if transmission and car.transmission != transmission:
            score += 1

        if condition and car.condition != condition:
            score += 1

        if city and car.city != city:
            score += 0.5

        return score

    candidates.sort(key=similarity_score)
    selected = candidates[:20]

    # با کمتر از ۳ آگهی مشابه، تخمین قابل اتکا نیست.
    if len(selected) < 3:
        return {
            "low": None,
            "median": None,
            "high": None,
            "sample_count": len(selected),
        }

    prices = sorted(int(car.price) for car in selected)
    low, _, high = quantiles(prices, n=4, method="inclusive")

    return {
        "low": round(low),
        "median": round(median(prices)),
        "high": round(high),
        "sample_count": len(prices),
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
    *, brand_id, model_name, year=None, city=None,
    heavy_type=None, load_capacity=None
):
    candidates = _base_candidates(
        HeavyVehicle, brand_id, model_name, year, city
    )

    if heavy_type:
        same_type = candidates.filter(heavy_type=heavy_type)
        if same_type.count() >= 3:
            candidates = same_type

    if load_capacity is not None:
        similar_capacity = candidates.filter(
            load_capacity__gte=load_capacity * 0.8,
            load_capacity__lte=load_capacity * 1.2,
        )
        if similar_capacity.count() >= 3:
            candidates = similar_capacity

    return _price_range(candidates)
