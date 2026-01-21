from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class PhoneRegisterForm(UserCreationForm):
    # فیلدهای اضافی
    phone = forms.CharField(
        max_length=11,
        required=True,
        label='شماره موبایل',
        widget=forms.TextInput(attrs={'placeholder': '09123456789'})
    )
    first_name = forms.CharField(required=True, label='نام')
    last_name = forms.CharField(required=True, label='نام خانوادگی')
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # username رو مخفی کن یا برچسبش رو تغییر بده
        self.fields['username'].label = 'ایمیل (برای ورود)'
        self.fields['username'].help_text = 'ایمیل خود را وارد کنید'
    
    def clean_username(self):
        # اگر username خالی بود، از phone استفاده کن
        username = self.cleaned_data.get('username')
        if not username:
            username = self.cleaned_data.get('phone')
        return username
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class':'form-control',
            'placeholder':'ایمیل خود را وارد کنید',
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=True, 
        widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'شماره تلفن',   
        })
                            
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget= forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'شهر',     
        })
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'city', 'password1', 'password2']
        
        widgets = {
            'username': forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'نام کاربری',    
            }),
        }


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            user.profile.phone = self.cleaned_data['phone']
            user.profile.city = self.cleaned_data['city']
            user.profile.save()
        return user
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class':'form-control'
        })
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username':forms.TextInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name':forms.TextInput(attrs={'class':'form-control'}),
        }
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'city', 'avatar', 'seller_bio']
        widgets = {
            'phone':forms.TextInput(attrs={'class':'form-control'}),
            'city': forms.TextInput(attrs={'class':'form-control'}),
            'seller_bio':forms.Textarea(attrs={
                'class':'form-control',
                'rows':4,
                'placeholder':'درباره خودتان بنویسید ....',
            }) ,
        }

