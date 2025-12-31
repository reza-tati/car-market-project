# cars/forms.py
from django import forms
from .models import Car, CarImage, Brand, CarModel
from django.forms import inlineformset_factory  # برای فرم‌های مرتبط

class CarForm(forms.ModelForm):
    """
    فرم ثبت و ویرایش خودرو
    """
    class Meta:
        model = Car
        # فیلدهایی که در فرم نمایش داده می‌شوند
        fields = [
            'title', 'brand', 'model', 'year', 'price', 'mileage',
            'color', 'transmission', 'fuel_type', 'engine_capacity',
            'engine_power', 'condition', 'has_insurance', 'insurance_expiry',
            'has_service_book', 'description', 'city', 'district', 'address'
        ]
        
        # تنظیمات widget ها برای ظاهر بهتر
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: پژو ۲۰۶ صفر - وضعیت عالی'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1360',  # حداقل سال
                'max': '1403'   # حداکثر سال
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
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'آدرس دقیق (اختیاری)'
            }),
            'insurance_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'  # استفاده از datepicker مرورگر
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """مقداردهی اولیه فرم"""
        super().__init__(*args, **kwargs)
        
        # مرتب‌سازی برندها
        self.fields['brand'].queryset = Brand.objects.all().order_by('name')
        
        # ابتدا مدل‌ها خالی هستند
        self.fields['model'].queryset = CarModel.objects.none()
        
        # اگر برند انتخاب شده، مدل‌های آن را بارگیری کن
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = CarModel.objects.filter(
                    brand_id=brand_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass  # اگر برند معتبر نیست، کاری نکن
        elif self.instance.pk:  # اگر در حال ویرایش هستیم
            if self.instance.brand:
                # مدل‌های برند انتخاب شده را نمایش بده
                self.fields['model'].queryset = self.instance.brand.models.all().order_by('name')
class CarImageForm(forms.ModelForm):
    """
    فرم آپلود تصویر خودرو
    """
    image = forms.ImageField(
        label='تصویر',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'  # فقط فایل‌های تصویری
        })
    )
    
    class Meta:
        model = CarImage
        fields = ['image', 'is_main']
        widgets = {
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
# 🔹 **Formset برای آپلود چند تصویر**
# یک فرم‌ست اجازه می‌دهد چند فرم از یک نوع را در یک صفحه داشته باشیم
CarImageFormSet = inlineformset_factory(
    Car,           # مدل اصلی
    CarImage,      # مدل مرتبط
    form=CarImageForm,  # فرم هر آیتم
    extra=5,       # ۵ فرم خالی اضافه کن
    max_num=10,    # حداکثر ۱۰ فرم
    can_delete=True  # امکان حذف آیتم‌ها
)