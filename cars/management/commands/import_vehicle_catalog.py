import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cars.models import VehicleCatalogModel, VehicleVariant


HEADERS = {
    "vehicle_type",
    "brand",
    "name",
    "category",
    "production_start_year",
    "production_end_year",
    "is_current",
    "variant_name",
    "variant_start_year",
    "variant_end_year",
    "variant_is_current",
}

DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def parse_year(value):
    value = (value or "").strip().translate(DIGITS)
    if not value or value in {"تاکنون", "اکنون", "present", "current"}:
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"سال نامعتبر است: {value!r}")


def parse_bool(value, default):
    value = (value or "").strip().lower()
    if not value:
        return default
    if value in {"true", "1", "yes", "بله"}:
        return True
    if value in {"false", "0", "no", "خیر"}:
        return False
    raise ValueError(f"مقدار بولی نامعتبر است: {value!r}")


class Command(BaseCommand):
    help = "Import vehicle models and variants from a CSV file"

    def add_arguments(self, parser):
        default_path = Path(settings.BASE_DIR) / "cars/data/vehicle_catalog.csv"
        parser.add_argument("--csv", default=str(default_path))

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["csv"])
        if not path.exists():
            raise CommandError(f"CSV file not found: {path}")

        brand_model = (
            VehicleCatalogModel._meta.get_field("brand").remote_field.model
        )
        valid_types = {
            value
            for value, label in VehicleCatalogModel._meta
            .get_field("vehicle_type").choices
        }

        imported_models = 0
        imported_variants = 0

        with path.open(encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            missing = HEADERS - set(reader.fieldnames or [])
            if missing:
                raise CommandError(
                    "Missing CSV columns: " + ", ".join(sorted(missing))
                )

            rows = list(reader)
            if not rows:
                raise CommandError("CSV has a header but no data rows.")

            for line, row in enumerate(rows, start=2):
                try:
                    vehicle_type = (row["vehicle_type"] or "").strip()
                    brand_name = (row["brand"] or "").strip()
                    name = (row["name"] or "").strip()
                    category = (row["category"] or "").strip()

                    if vehicle_type not in valid_types:
                        raise ValueError(
                            f"vehicle_type باید یکی از این‌ها باشد: "
                            f"{sorted(valid_types)}"
                        )
                    if not brand_name or not name or not category:
                        raise ValueError(
                            "brand، name و category نباید خالی باشند"
                        )

                    brand = brand_model.objects.get(name=brand_name)

                    start_year = parse_year(row["production_start_year"])
                    end_year = parse_year(row["production_end_year"])
                    is_current = parse_bool(
                        row["is_current"], default=(end_year is None)
                    )

                    catalog_model, _ = VehicleCatalogModel.objects.update_or_create(
                        vehicle_type=vehicle_type,
                        brand=brand,
                        name=name,
                        defaults={
                            "category": category,
                            "production_start_year": start_year,
                            "production_end_year": end_year,
                            "is_current": is_current,
                            "is_active": True,
                        },
                    )
                    imported_models += 1

                    variant_name = (row["variant_name"] or "").strip()
                    if variant_name:
                        variant_start = parse_year(row["variant_start_year"])
                        variant_end = parse_year(row["variant_end_year"])
                        variant_current = parse_bool(
                            row["variant_is_current"],
                            default=(variant_end is None),
                        )

                        VehicleVariant.objects.update_or_create(
                            catalog_model=catalog_model,
                            name=variant_name,
                            defaults={
                                "production_start_year": variant_start,
                                "production_end_year": variant_end,
                                "is_current": variant_current,
                                "is_active": True,
                            },
                        )
                        imported_variants += 1

                except brand_model.DoesNotExist:
                    raise CommandError(
                        f"CSV line {line}: brand {brand_name!r} not found"
                    )
                except (ValueError, TypeError, KeyError) as exc:
                    raise CommandError(f"CSV line {line}: {exc}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported/updated {imported_models} model rows and "
                f"{imported_variants} variants."
            )
        )
