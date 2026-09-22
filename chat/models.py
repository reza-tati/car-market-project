# chat/models.py
from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    """
    مدل اتاق چت بین دو کاربر (خریدار و فروشنده)
    """
    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='chat_rooms_as_user1', verbose_name='کاربر اول'
    )
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='chat_rooms_as_user2', verbose_name='کاربر دوم'
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=[('car', 'سواری'), ('motorcycle', 'موتورسیکلت'), ('heavy', 'سنگین')],
        default='car', verbose_name='نوع وسیله نقلیه'
    )
    vehicle_id = models.PositiveIntegerField(verbose_name='شناسه وسیله نقلیه')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'اتاق چت'
        verbose_name_plural = 'اتاق‌های چت'
        ordering = ['-updated_at']
        unique_together = ['user1', 'user2', 'vehicle_type', 'vehicle_id']
    
    def __str__(self):
        return f"چت {self.user1.username} و {self.user2.username}"
    
    def get_other_user(self, current_user):
        if self.user1 == current_user:
            return self.user2
        return self.user1
    
    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()
    
    def get_unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """
    مدل پیام‌های چت (متن + عکس)
    """
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE,
        related_name='messages', verbose_name='اتاق چت'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='sent_messages', verbose_name='فرستنده'
    )
    
    # ✅ متن پیام (اختیاری - می‌تونه فقط عکس باشه)
    text = models.TextField(blank=True, null=True, verbose_name='متن پیام')
    
    # ✅ عکس پیام (اختیاری - می‌تونه فقط متن باشه)
    image = models.ImageField(
        upload_to='chat/images/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name='تصویر'
    )
    
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='زمان ارسال')
    
    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'
        ordering = ['timestamp']
    
    def __str__(self):
        if self.text:
            return f"{self.sender.username}: {self.text[:30]}"
        return f"{self.sender.username}: [تصویر]"
    
    def is_image(self):
        """آیا پیام عکس داره؟"""
        return bool(self.image)
    
    def get_display_text(self):
        """متن نمایشی پیام"""
        if self.text:
            return self.text
        return '📷 تصویر'