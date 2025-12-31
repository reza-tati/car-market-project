# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='شماره تلفن')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='تصویر پروفایل')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='شهر')
    
    # اطلاعات فروشنده
    is_seller = models.BooleanField(default=False, verbose_name='فروشنده است؟')
    seller_rating = models.FloatField(default=0.0, verbose_name='امتیاز فروشنده')
    seller_bio = models.TextField(blank=True, null=True, verbose_name='درباره فروشنده')
    
    # آمار
    total_listings = models.IntegerField(default=0, verbose_name='تعداد آگهی‌ها')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل کاربران'
    
    def __str__(self):
        return f"{self.user.username} - {self.user.get_full_name()}"
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

# سیگنال‌ها برای ایجاد پروفایل به‌طور خودکار
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# Create your models here.
