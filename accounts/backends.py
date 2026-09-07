# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # جستجوی کاربر بر اساس شماره موبایل در پروفایل
            user = User.objects.get(profile__phone=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None