# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # ✅ استفاده از filter به جای get (برای جلوگیری از MultipleObjectsReturned)
            users = User.objects.filter(profile__phone=username)
            
            if not users.exists():
                return None
            
            # اگه چند کاربر با این شماره وجود داشت، جدیدترین رو انتخاب کن
            if users.count() > 1:
                user = users.order_by('-date_joined').first()
                print(f"⚠️ هشدار: {users.count()} کاربر با شماره {username} وجود داره. جدیدترین انتخاب شد.")
            else:
                user = users.first()
            
            # بررسی رمز عبور
            if user.check_password(password):
                return user
            
            return None
        
        except Exception as e:
            print(f"❌ خطا در احراز هویت: {e}")
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None