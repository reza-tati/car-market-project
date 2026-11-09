import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from django.utils.text import slugify

from cars.models import (
    Brand,
    Car,
    CarModel,
    HeavyVehicle,
    Motorcycle,
    VehicleCatalogModel,
    VehicleVariant,
)


VEHICLE_TYPES = {
    Car: "car",
    Motorcycle: "motorcycle",
    HeavyVehicle: "heavy",
}

CITIES = ["تهران", "کرج", "اصفهان", "شیراز", "مشهد"]


def choice_value(field):
    """اولین گزینهٔ غیرخالی را از فیلد دارای choices برمی‌گرداند."""
    def flatten(choices):
        for value, label in choices:
            if isinstance(label, (list, tuple)):
                yield from flatten(label)
            else:
                yield value

    for value in flatten(field.choices):
        if value not in ("", None):
            return value
    return None


def related_object(field, vehicle_type, catalog_model=None):
    """یک نمونهٔ مناسب از مدل مرتبط پیدا می‌کند."""
    related_model = field.remote_field.model
    field_name = field.name

    if related_model == get_user_model() or field_name in {"seller", "user"}:
        users = related_model.objects.all()
        user = users.filter(is_staff=True).first() or users.first()
        if user is None and not field.null and not field.blank:
            raise CommandError(
                "برای ساخت آگهی، حداقل یک کاربر باید در دیتابیس موجود باشد."
            )
        return user

    if related_model == VehicleVariant or field_name == "catalog_variant":
        variants = related_model.objects.filter(is_active=True)
        if catalog_model is not None:
            variants = variants.filter(catalog_model=catalog_model)
        return variants.first()

    if related_model == VehicleCatalogModel or field_name == "catalog_model":
        return related_model.objects.filter(
            vehicle_type=vehicle_type,
            is_active=True,
        ).first()

    if related_model == Brand or field_name == "brand":
        brands = related_model.objects.all()
        if any(f.name == "vehicle_type" for f in related_model._meta.fields):
            brands = brands.filter(vehicle_type=vehicle_type)
        return brands.first()

    # برای روابط قدیمی، مثل Car.model، از اولین رکورد موجود استفاده می‌کنیم.
    objects = related_model.objects.all()

    if any(f.name == "brand" for f in related_model._meta.fields):
        if catalog_model and hasattr(catalog_model, "brand_id"):
            objects = objects.filter(brand_id=catalog_model.brand_id)

    return objects.first()


def value_for_field(field, index, vehicle_type, catalog_model=None):
    name = field.name.lower()

    if name == "vehicle_type":
        return vehicle_type

    if name in {"title", "name"}:
        return f"آگهی آزمایشی {vehicle_type} {index + 1}"

    if name == "slug":
        return slugify(f"demo-{vehicle_type}-{index}-{uuid.uuid4().hex[:8]}")

    if name in {"description", "details"}:
        return "این آگهی برای آزمایش و بررسی عملکرد سایت ثبت شده است."

    if name in {"city", "location"}:
        if isinstance(field, models.CharField):
            return CITIES[index % len(CITIES)]

    if name in {"price", "amount"}:
        return Decimal(500_000_000 + index * 25_000_000)

    if name in {"year", "production_year", "manufacture_year"}:
        return 1402 - (index % 8)

    if name in {"mileage", "kilometer", "kilometers"}:
        return 20_000 + index * 12_000

    if name in {"is_active"}:
        return True

    if name in {"is_draft", "is_sold", "is_current"}:
        return False

    if name in {"transmission", "gearbox"}:
        if field.choices:
            return choice_value(field)

    if name in {"body_condition", "condition"}:
        if field.choices:
            return choice_value(field)

    if field.choices:
        return choice_value(field)

    if isinstance(field, models.BooleanField):
        return False

    if isinstance(field, (models.IntegerField, models.BigIntegerField)):
        return 1

    if isinstance(field, models.DecimalField):
        return Decimal("1")

    if isinstance(field, models.FloatField):
        return 1.0

    if isinstance(field, models.CharField):
        if field.max_length and field.max_length < 8:
            return "demo"[:field.max_length]
        return f"آزمایشی {index + 1}"

    return None


def build_vehicle_data(model_class, vehicle_type, index):
    data = {}
    catalog_model = None

    # ابتدا مدل کاتالوگ را پیدا می‌کنیم تا variant و brand با آن هماهنگ باشند.
    catalog_field = next(
        (
            field
            for field in model_class._meta.fields
            if field.name == "catalog_model"
            and isinstance(field, models.ForeignKey)
        ),
        None,
    )
    if catalog_field:
        catalog_model = related_object(catalog_field, vehicle_type)

    for field in model_class._meta.fields:
        if (
            field.primary_key
            or field.auto_created
            or field.name in {"created_at", "updated_at"}
            or getattr(field, "auto_now", False)
            or getattr(field, "auto_now_add", False)
            or field.has_default()
        ):
            continue

        if isinstance(field, models.ForeignKey):
            related = related_object(field, vehicle_type, catalog_model)
            if related is not None:
                data[field.name] = related
            elif not field.null and not field.blank:
                raise CommandError(
                    f"برای فیلد اجباری {model_class.__name__}.{field.name} "
                    "رکورد مرتبطی پیدا نشد. ابتدا کاتالوگ، برندها و داده‌های لازم را وارد کنید."
                )
            continue

        if field.blank or field.null:
            # برای فیلدهای اختیاری فقط مقادیر مشخص و مفید را تنظیم می‌کنیم.
            if field.name in {"is_active", "is_draft", "is_sold"}:
                data[field.name] = value_for_field(
                    field, index, vehicle_type, catalog_model
                )
            continue

        value = value_for_field(field, index, vehicle_type, catalog_model)
        if value is not None:
            data[field.name] = value

    # اگر مدل قدیمیِ Car فیلد model اجباری داشته باشد، build_vehicle_data
    # آن را از رکوردهای موجود پر می‌کند؛ در غیر این صورت نیازی به آن نیست.
    return data


class Command(BaseCommand):
    help = "ساخت آگهی‌های آزمایشی برای خودرو، موتورسیکلت و ماشین سنگین"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=3,
            help="تعداد آگهی برای هر نوع وسیله (پیش‌فرض: 3)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        if count < 1:
            raise CommandError("--count باید عددی بزرگ‌تر از صفر باشد.")

        total = 0

        for model_class, vehicle_type in VEHICLE_TYPES.items():
            for index in range(count):
                data = build_vehicle_data(model_class, vehicle_type, index)
                model_class.objects.create(**data)
                total += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"{count} آگهی آزمایشی برای {model_class.__name__} ساخته شد."
                )
            )

        self.stdout.write(self.style.SUCCESS(f"مجموع آگهی‌های ساخته‌شده: {total}"))
