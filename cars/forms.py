from django import forms
from django.forms import inlineformset_factory
from .models import Car, CarImage, Brand, CarModel

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'title', 'brand', 'model', 'year', 'price', 'mileage',
            'color', 'transmission', 'fuel_type', 'engine_capacity',
            'condition', 'description', 'city'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: سمند LX مدل ۱۴۰۰ - وضعیت عالی'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1360',
                'max': '1405'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'قیمت به تومان'
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'کارکرد به کیلومتر'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'توضیحات کامل درباره خودرو...'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شهر'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # مرتب‌سازی برندها67iop sz
        self.fields['brand'].queryset = Brand.objects.all().order_by('name')
        
        # ابتدا مدل‌ها خالی
        self.fields['model'].queryset = CarModel.objects.none()
        
        # اگر برند انتخاب شده
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = CarModel.objects.filter(
                    brand_id=brand_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            if self.instance.brand:
                self.fields['model'].queryset = self.instance.brand.models.all().order_by('name')

class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_main': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

# Formset برای آپلود چند تصویر
CarImageFormSet = inlineformset_factory(
    Car,
    CarImage,
    form=CarImageForm,
    extra=3,  # ۳ فرم خالی اولیه
    max_num=10,  # حداکثر ۱۰ تصویر
    can_delete=True  # امکان حذف
)