# payments/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Payment(models.Model):
    """
    مدل تراکنش‌های پرداخت
    """
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
        ('canceled', 'لغو شده'),
    ]
    
    VEHICLE_TYPE_CHOICES = [
        ('car', 'سواری'),
        ('motorcycle', 'موتورسیکلت'),
        ('heavy', 'ماشین سنگین'),
    ]
    
    # کاربر پرداخت‌کننده
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='کاربر'
    )
    
    # اطلاعات آگهی
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        verbose_name='نوع وسیله نقلیه'
    )
    vehicle_id = models.PositiveIntegerField(
        verbose_name='شناسه وسیله نقلیه'
    )
    
    # مبلغ
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ (تومان)'
    )
    
    # وضعیت
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # اطلاعات تراکنش
    tracking_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name='کد پیگیری'
    )
    gateway_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='نام درگاه'
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شماره مرجع'
    )
    
    # اطلاعات اضافی
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
    )
    
    # زمان‌ها
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ پرداخت'
    )
    
    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.amount:,} تومان - {self.get_status_display()}"
    
    def is_successful(self):
        """آیا پرداخت موفق بوده؟"""
        return self.status == 'success'
    
    def mark_as_success(self, reference_id=None):
        """علامت‌گذاری به عنوان موفق"""
        self.status = 'success'
        self.paid_at = timezone.now()
        if reference_id:
            self.reference_id = reference_id
        self.save()
    
    def mark_as_failed(self, description=None):
        """علامت‌گذاری به عنوان ناموفق"""
        self.status = 'failed'
        if description:
            self.description = description
        self.save()