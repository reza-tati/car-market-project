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
        widget=forms.TextInput(attrs={
             'class': 'form-control',
            'placeholder': '09123456789'})
    )
    first_name = forms.CharField(
        required=True,
        label='نام',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'علی'
        })
    )
    last_name = forms.CharField(
        required=True,
        label='نام خانوادگی',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'محمدی'
        })
    )
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        required=True,
        label='نوع حساب کاربری',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'phone', 'password1', 'password2', 'user_type']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
         # مخفی کردن فیلد username (چون از شماره موبایل استفاده میکنیم)
        self.fields['username'].widget = forms.HiddenInput()
        self.fields['username'].required = False
        
        # تغییر ظاهر فیلدهای رمز عبور
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رمز عبور را وارد کنید'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'تکرار رمز عبور'
        })
        
        # حذف help_text های اضافی
        self.fields['password1'].help_text = 'رمز عبور باید حداقل ۸ کاراکتر و شامل حروف و اعداد باشد'
        self.fields['password2'].help_text = ''

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(profile__phone=phone).exists():
            raise forms.ValidationError('این شماره موبایل قبلاً ثبت شده است!')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            
            # ایجاد یا به‌روزرسانی پروفایل
            profile = user.profile
            profile.phone = self.cleaned_data['phone']
            profile.user_type = self.cleaned_data['user_type']
            
            # اگر کاربر نوع فروشنده رو انتخاب کرده
            if self.cleaned_data['user_type'] == 'seller':
                profile.is_seller = True
            else:
                profile.is_seller = False
            
            profile.save()
        return user
# class UserRegisterForm(UserCreationForm):
#     email = forms.EmailField(
#         required=True,
#         widget=forms.EmailInput(attrs={
#             'class':'form-control',
#             'placeholder':'ایمیل خود را وارد کنید',
#         })
#     )
#     phone = forms.CharField(
#         max_length=15,
#         required=True, 
#         widget=forms.TextInput(attrs={
#         'class':'form-control',
#         'placeholder':'شماره تلفن',   
#         })
                            
#     )
#     city = forms.CharField(
#         max_length=100,
#         required=False,
#         widget= forms.TextInput(attrs={
#         'class':'form-control',
#         'placeholder':'شهر',     
#         })
#     )
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'phone', 'city', 'password1', 'password2']
        
#         widgets = {
#             'username': forms.TextInput(attrs={
#             'class':'form-control',
#             'placeholder':'نام کاربری',    
#             }),
#         }


#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data['email']

#         if commit:
#             user.save()
#             user.profile.phone = self.cleaned_data['phone']
#             user.profile.city = self.cleaned_data['city']
#             user.profile.save()
#         return user
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

