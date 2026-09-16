# cars/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Car, Motorcycle, HeavyVehicle, CarImage, Brand, CarModel, MotorcycleImage, HeavyVehicleImage


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'title', 'brand', 'model', 'year', 'price', 'mileage',
            'color', 'transmission', 'fuel_type', 'engine_capacity',
            'condition', 'description', 'city'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: سمند LX مدل ۱۴۰۰'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1360', 'max': '1405'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قیمت به تومان'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'کارکرد به کیلومتر'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شهر'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].queryset = Brand.objects.all().order_by('name')
        self.fields['model'].queryset = CarModel.objects.none()
        
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = CarModel.objects.filter(
                    brand_id=brand_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.brand:
            self.fields['model'].queryset = self.instance.brand.models.all().order_by('name')


# cars/forms.py

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
            'is_featured',      # پیش‌فرض False
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: هوندا CB400'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1360', 'max': '1405'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'کارکرد به کیلومتر'}),
            'engine_cc': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'حجم موتور به سی‌سی'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شهر'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قیمت به تومان'}),
        }


class HeavyVehicleForm(forms.ModelForm):
    class Meta:
        model = HeavyVehicle
        # ✅ همه فیلدهای خودکار و غیرضروری رو exclude کن
        exclude = [
            'seller',
            'vehicle_type',
            'slug',
            'views',
            'phone_views',
            'created_at',       # ✅ این خیلی مهمه
            'updated_at',       # ✅ این هم همینطور
            'is_sold',
            'is_active',
            'is_verified',
            'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: کامیون ولوو'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1360', 'max': '1405'}),
            'load_capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ظرفیت بار به تن'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شهر'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قیمت به تومان'}),
        }


# cars/forms.py
from .models import Car, Motorcycle, HeavyVehicle, CarImage, MotorcycleImage, HeavyVehicleImage, Brand, CarModel


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