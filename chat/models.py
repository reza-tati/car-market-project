# chat/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatRoom(models.Model):
    """
    مدل اتاق چت بین دو کاربر (خریدار و فروشنده)
    """
    # کاربر اول (معمولاً خریدار)
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_rooms_as_user1',
        verbose_name='کاربر اول'
    )
    
    # کاربر دوم (معمولاً فروشنده)
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_rooms_as_user2',
        verbose_name='کاربر دوم'
    )
    
    # نوع وسیله نقلیه (car, motorcycle, heavy)
    vehicle_type = models.CharField(
        max_length=20,
        choices=[
            ('car', 'سواری'),
            ('motorcycle', 'موتورسیکلت'),
            ('heavy', 'سنگین'),
        ],
        default='car',
        verbose_name='نوع وسیله نقلیه'
    )
    
    # شناسه وسیله نقلیه
    vehicle_id = models.PositiveIntegerField(
        verbose_name='شناسه وسیله نقلیه'
    )
    
    # زمان ساخت
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    # زمان آخرین پیام
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    
    class Meta:
        verbose_name = 'اتاق چت'
        verbose_name_plural = 'اتاق‌های چت'
        ordering = ['-updated_at']
        # جلوگیری از ساخت اتاق تکراری
        unique_together = ['user1', 'user2', 'vehicle_type', 'vehicle_id']
    
    def __str__(self):
        return f"چت {self.user1.username} و {self.user2.username} - {self.vehicle_type}"
    
    def get_other_user(self, current_user):
        """دریافت کاربر مقابل"""
        if self.user1 == current_user:
            return self.user2
        return self.user1
    
    def get_last_message(self):
        """دریافت آخرین پیام"""
        return self.messages.order_by('-timestamp').first()
    
    def get_unread_count(self, user):
        """تعداد پیام‌های خوانده نشده برای کاربر"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """
    مدل پیام‌های چت
    """
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='اتاق چت'
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='فرستنده'
    )
    
    text = models.TextField(
        verbose_name='متن پیام'
    )
    
    # وضعیت خوانده شدن
    is_read = models.BooleanField(
        default=False,
        verbose_name='خوانده شده'
    )
    
    # زمان ارسال
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ارسال'
    )
    
    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.text[:50]}"