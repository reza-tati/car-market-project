# search/forms.py
from django import forms
from cars.models import Brand, CarModel, Car

class AdvancedSearchForm(forms.Form):
    """
    فرم جستجوی پیشرفته با فیلترهای متعدد
    """
    query = forms.CharField(
        required=False,  # اجباری نیست
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'جستجوی خودرو...',
            'id': 'search-input'
        }),
        label=''  # بدون لیبل
    )
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        empty_label="همه برندها",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    model = forms.ModelChoiceField(
        queryset=CarModel.objects.none(),  # ابتدا خالی
        required=False,
        empty_label="همه مدل‌ها",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_year = forms.IntegerField(
        required=False,
        min_value=1360,
        max_value=1403,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'از سال'
        })
    )
    
    max_year = forms.IntegerField(
        required=False,
        min_value=1360,
        max_value=1403,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'تا سال'
        })
    )
    
    min_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'حداقل قیمت'
        })
    )
    
    max_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'حداکثر قیمت'
        })
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'شهر'
        })
    )
    
    # استفاده از CHOICES های مدل Car
    transmission = forms.ChoiceField(
        choices=[('', 'همه')] + list(Car.TRANSMISSION_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fuel_type = forms.ChoiceField(
        choices=[('', 'همه')] + list(Car.FUEL_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )