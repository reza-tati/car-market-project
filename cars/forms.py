# cars/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Car, Motorcycle, HeavyVehicle, CarImage, Brand, CarModel, MotorcycleImage, HeavyVehicleImage, VehicleVariant, VehicleCatalogModel


class CarForm(forms.ModelForm):
    catalog_model = forms.ModelChoiceField(
        queryset=VehicleCatalogModel.objects.none(),
        label="مدل",
    )
    catalog_variant = forms.ModelChoiceField(
        queryset=VehicleVariant.objects.none(),
        required=False,
        label="تیپ",
    )

    class Meta:
        model = Car
        fields = [
            "title", "brand", "catalog_model", "catalog_variant",
            "year", "price", "mileage", "color", "transmission",
            "fuel_type", "engine_capacity", "condition",
            "description", "city",
        ]
        widgets = {
            "brand": forms.Select(attrs={"class": "form-select"}),
            "catalog_model": forms.Select(attrs={"class": "form-select"}),
            "catalog_variant": forms.Select(attrs={"class": "form-select"}),
            "color": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "مثال: سمند LX مدل ۱۴۰۰",
            }),
            "year": forms.NumberInput(attrs={
                "class": "form-control", "min": "1360", "max": "1405",
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control", "placeholder": "قیمت به تومان",
            }),
            "mileage": forms.NumberInput(attrs={
                "class": "form-control", "placeholder": "کارکرد به کیلومتر",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control", "rows": 4,"placeholder": "وضعیت فنی و بدنه، رنگ‌شدگی یا تصادف، سرویس‌های انجام‌شده و ایرادهای خودرو را بنویسید...",
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "شهر",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].help_text = (
    "واضح بنویسید تا خریداران سؤال تکراری کمتری بپرسند."
)

        self.fields["brand"].queryset = Brand.objects.filter(
            vehicle_catalog_models__vehicle_type="car",
            vehicle_catalog_models__is_active=True,
        ).distinct().order_by("name")

        self.fields["catalog_model"].queryset = (
            VehicleCatalogModel.objects.filter(
                vehicle_type="car",
                is_active=True,
            ).select_related("brand")
        )

        brand_id = self.data.get("brand") or self.instance.brand_id
        if brand_id:
            self.fields["catalog_model"].queryset = (
                self.fields["catalog_model"].queryset.filter(
                    brand_id=brand_id
                )
            )
        else:
            self.fields["catalog_model"].queryset = (
                VehicleCatalogModel.objects.none()
            )

        catalog_model_id = (
            self.data.get("catalog_model")
            or self.instance.catalog_model_id
        )

        if catalog_model_id:
            variants = VehicleVariant.objects.filter(
                catalog_model_id=catalog_model_id,
                is_active=True,
            )
            self.fields["catalog_variant"].queryset = variants
            self.fields["catalog_variant"].required = variants.exists()

    def save(self, commit=True):
        car = super().save(commit=False)
        car.vehicle_type = "car"

        if car.catalog_model_id:
            car.brand = car.catalog_model.brand
            car.model = CarModel.objects.filter(
                brand=car.brand,
                name=car.catalog_model.name,
            ).first()

        if commit:
            car.save()
            self.save_m2m()

        return car

class MotorcycleForm(forms.ModelForm):
    class Meta:
        model = Motorcycle
        # ✅ همه فیلدهای خودکار و غیرضروری رو exclude کن
        exclude = [
            'seller',           # خودکار تنظیم میشه
            'vehicle_type',     # خودکار تنظیم میشه
            'slug',             # خودکار تولید میشه
            'views',            # خودکار
            'phone_views',      # خودکار
            'created_at',       # ✅ این خیلی مهمه - خودکار پر میشه
            'updated_at',       # ✅ این هم همینطور
            'is_sold',          # پیش‌فرض False
            'is_active',        # پیش‌فرض True
            'is_verified',      # پیش‌فرض False
            'is_featured',
            'is_draft',              # ← جدید
            'draft_token',           # ← جدید
            'is_paid',               # ← جدید
            'payment_amount',        # ← جدید (مشکل اینجا بود!)
            'payment_date',          # ← جدید
            'payment_tracking_code', # ← جدید      # پیش‌فرض False
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: هوندا CB400'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1360', 'max': '1405'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'کارکرد به کیلومتر'}),
            'engine_cc': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'حجم موتور به سی‌سی'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'وضعیت فنی و بدنه، سرویس‌های انجام‌شده، لوازم جانبی و ایرادهای موتورسیکلت را بنویسید...',}),
            
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شهر'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قیمت به تومان'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].help_text = (
    "واضح بنویسید تا خریداران سؤال تکراری کمتری بپرسند."
)

        self.fields["brand"].queryset = Brand.objects.filter(
            vehicle_catalog_models__vehicle_type="motorcycle",
            vehicle_catalog_models__is_active=True,
        ).distinct().order_by("name")

class HeavyVehicleForm(forms.ModelForm):
    class Meta:
        model = HeavyVehicle
        exclude = [
            'seller', 'vehicle_type', 'slug', 'views', 'phone_views',
            'created_at', 'updated_at',
            'is_sold', 'is_active', 'is_verified', 'is_featured','is_draft',              # ← جدید
            'draft_token',           # ← جدید
            'is_paid',               # ← جدید
            'payment_amount',        # ← جدید (مشکل اینجا بود!)
            'payment_date',          # ← جدید
            'payment_tracking_code', # ← جدید
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: کامیون ولوو'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1360', 'max': '1410'}),
            'load_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'فقط عدد (مثال: 10)',
                'min': '0',
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,  "placeholder": (
        "چه قطعاتی تعویض شده؟\n"
        "کارشناسی شده؟\n"
        "دست چندم است؟ پلاک عرضه می‌شود؟\n"
        "معاوضه با چه ماشینی؟"
        "وضعیت فنی و بدنه؟ رنگ‌شدگی یا تصادف؟ سرویس‌های انجام‌شده ؟ ایرادهای خودرو؟"
    ),}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شهر'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قیمت به تومان'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].help_text = (
    "واضح بنویسید تا خریداران سؤال تکراری کمتری بپرسند."
)

        self.fields["brand"].queryset = Brand.objects.filter(
            vehicle_catalog_models__vehicle_type="heavy",
            vehicle_catalog_models__is_active=True,
        ).distinct().order_by("name")

# ===== فرم‌های تصویر =====
class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class MotorcycleImageForm(forms.ModelForm):
    class Meta:
        model = MotorcycleImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class HeavyVehicleImageForm(forms.ModelForm):
    class Meta:
        model = HeavyVehicleImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

# ===== Formsets =====
CarImageFormSet = inlineformset_factory(
    Car, CarImage,
    form=CarImageForm,
    extra=3, max_num=7, can_delete=True,
)

MotorcycleImageFormSet = inlineformset_factory(
    Motorcycle, MotorcycleImage,
    form=MotorcycleImageForm,
    extra=3, max_num=7, can_delete=True,
)

HeavyVehicleImageFormSet = inlineformset_factory(
    HeavyVehicle, HeavyVehicleImage,
    form=HeavyVehicleImageForm,
    extra=3, max_num=7, can_delete=True,
)