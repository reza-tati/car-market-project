# cars/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # برای زمان‌بندی
from django.urls import reverse  # برای تولید URL
from django.utils.text import slugify  # برای ایجاد slug از عنوان

class Brand(models.Model):
    """
    مدل برند خودرو (مثل پراید، پژو، ...)
    """
    name = models.CharField(
        max_length=100, 
        unique=True,  # نام تکراری نباشد
        verbose_name='نام برند'
    )
    
    logo = models.ImageField(
        upload_to='brands/logos/', 
        blank=True, 
        null=True, 
        verbose_name='لوگو'
    )
    
    country = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name='کشور سازنده'
    )
    
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='توضیحات'
    )
    
    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'
        ordering = ['name']  # مرتب‌سازی بر اساس نام
    
    def __str__(self):
        return self.name
class CarModel(models.Model):
    """
    مدل خودرو (مثل ۲۰۶، ۴۰۵، ...)
    رابطه چند به یک با برند دارد
    """
    # هر مدل متعلق به یک برند است
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.CASCADE,  # اگر برند حذف شد، مدل‌ها هم حذف شوند
        related_name='models',  # دسترسی از طریق brand.models
        verbose_name='برند'
    )
    
    name = models.CharField(max_length=100, verbose_name='نام مدل')
    
    production_years = models.CharField(
        max_length=50, 
        verbose_name='سال‌های تولید'
    )
    
    # انتخاب‌های ثابت برای دسته‌بندی
    CATEGORY_CHOICES = [
        ('sedan', 'سدان'),
        ('hatchback', 'هاچ‌بک'),
        ('suv', 'شاسی‌بلند'),
        ('pickup', 'وانت'),
        ('coupe', 'کوپه'),
        ('convertible', 'کروک'),
    ]
    
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES,  # لیست انتخاب‌ها
        default='sedan', 
        verbose_name='دسته‌بندی'
    )
    
    class Meta:
        verbose_name = 'مدل خودرو'
        verbose_name_plural = 'مدل خودروها'
        ordering = ['brand', 'name']
        unique_together = ['brand', 'name']  # ترکیب برند و مدل منحصربه‌فرد باشد
    
    def __str__(self):
        return f"{self.brand.name} {self.name}"
class Car(models.Model):
    """
    مدل اصلی خودرو (آگهی)
    شامل تمام اطلاعات یک خودرو برای فروش
    """
    
    # 🔹 **انتخاب‌های ثابت (CHOICES)**
    # برای فیلدهایی که مقدار ثابتی دارند
    
    # وضعیت بدنه
    CONDITION_CHOICES = [
        ('excellent', 'عالی'),
        ('good', 'خوب'),
        ('average', 'متوسط'),
        ('damaged', 'آسیب‌دیده'),
        ('accident', 'تصادفی'),
    ]
    
    # نوع گیربکس
    TRANSMISSION_CHOICES = [
        ('manual', 'دستی'),
        ('automatic', 'اتوماتیک'),
        ('cvt', 'CVT'),
        ('dual_clutch', 'دوکلاچه'),
    ]

      # نوع سوخت
    FUEL_CHOICES = [
        ('petrol', 'بنزینی'),
        ('diesel', 'دیزل'),
        ('hybrid', 'هیبرید'),
        ('electric', 'الکتریکی'),
        ('cng', 'گازسوز'),
    ]
    
    # رنگ‌ها
    COLOR_CHOICES = [
        ('white', 'سفید'),
        ('black', 'مشکی'),
        ('silver', 'نقره‌ای'),
        ('gray', 'خاکستری'),
        ('red', 'قرمز'),
        ('blue', 'آبی'),
        ('green', 'سبز'),
        ('brown', 'قهوه‌ای'),
        ('yellow', 'زرد'),
        ('orange', 'نارنجی'),
    ]

        # 🔹 **اطلاعات اصلی خودرو**
    
    # فروشنده - رابطه با مدل User
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # اگر کاربر حذف شد، آگهی‌هایش هم حذف شوند
        related_name='cars',  # دسترسی از طریق user.cars
        verbose_name='فروشنده'
    )
    
    title = models.CharField(max_length=200, verbose_name='عنوان آگهی')
    
    # Slug برای URL زیبا: پراید-۲۰۶-۱۴۰۰
    slug = models.SlugField(
        max_length=250, 
        unique_for_date='created_at',  # منحصربه‌فرد در هر تاریخ
        blank=True  # در فرم اجباری نیست
    )
    
    # برند و مدل - رابطه با مدل‌های Brand و CarModel
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.SET_NULL,  # اگر برند حذف شد، null شود
        null=True, 
        verbose_name='برند'
    )
    
    model = models.ForeignKey(
        CarModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='مدل'
    )
    
    year = models.PositiveIntegerField(verbose_name='سال ساخت')
    price = models.DecimalField(
        max_digits=15,  # حداکثر ۱۵ رقم
        decimal_places=0,  # بدون اعشار (تومان)
        verbose_name='قیمت (تومان)'
    )
    mileage = models.PositiveIntegerField(verbose_name='کارکرد (کیلومتر)')

     # 🔹 **مشخصات فنی**
    
    # استفاده از choices برای نمایش فارسی
    color = models.CharField(
        max_length=50, 
        choices=COLOR_CHOICES, 
        verbose_name='رنگ'
    )
    
    transmission = models.CharField(
        max_length=20, 
        choices=TRANSMISSION_CHOICES, 
        verbose_name='گیربکس'
    )
    
    fuel_type = models.CharField(
        max_length=20, 
        choices=FUEL_CHOICES, 
        verbose_name='نوع سوخت'
    )
    
    engine_capacity = models.PositiveIntegerField(
        verbose_name='حجم موتور (سی‌سی)'
    )
    
    engine_power = models.PositiveIntegerField(
        verbose_name='قدرت موتور (اسب)', 
        blank=True, 
        null=True  # اختیاری
    )
    
      # 🔹 **وضعیت خودرو**
    
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        verbose_name='وضعیت بدنه'
    )
    
    has_insurance = models.BooleanField(
        default=False, 
        verbose_name='بیمه دارد'
    )
    
    insurance_expiry = models.DateField(
        blank=True, 
        null=True, 
        verbose_name='تاریخ انقضای بیمه'
    )
    
    has_service_book = models.BooleanField(
        default=False, 
        verbose_name='دفترچه سرویس دارد'
    )
    
    description = models.TextField(verbose_name='توضیحات')
    
       # 🔹 **اطلاعات مکانی**
    
    city = models.CharField(max_length=100, verbose_name='شهر')
    district = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='منطقه'
    )
    address = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='آدرس دقیق'
    )

     # 🔹 **وضعیت آگهی**
    
    is_sold = models.BooleanField(default=False, verbose_name='فروخته شده')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    is_featured = models.BooleanField(default=False, verbose_name='آگهی ویژه')
    
    # 🔹 **زمان‌های سیستمی**
    
    created_at = models.DateTimeField(
        default=timezone.now,  # زمان فعلی
        verbose_name='تاریخ ثبت'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,  # هر بار ذخیره به‌روز شود
        verbose_name='آخرین بروزرسانی'
    )
    
    # 🔹 **شمارنده‌ها (برای آمار)**
    
    views = models.PositiveIntegerField(
        default=0, 
        verbose_name='تعداد بازدید'
    )
    
    phone_views = models.PositiveIntegerField(
        default=0, 
        verbose_name='تعداد نمایش شماره'
    )


    class Meta:
        """تنظیمات متا برای مدل"""
        verbose_name = 'خودرو'
        verbose_name_plural = 'خودروها'
        ordering = ['-created_at']  # جدیدترین اول
        
        # ایجاد ایندکس برای جستجوی سریع‌تر
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['price']),
            models.Index(fields=['city']),
            models.Index(fields=['is_active', 'is_verified']),
        ]
    
    def __str__(self):
        """نمایش رشته‌ای مدل"""
        return f"{self.brand.name if self.brand else ''} {self.model.name if self.model else ''} - {self.year}"
    
    def save(self, *args, **kwargs):
        """ذخیره مدل با ایجاد خودکار slug"""
        if not self.slug:  # اگر slug نداریم
            # ایجاد slug از ترکیب برند-مدل-سال
            base_slug = slugify(f"{self.brand.name}-{self.model.name}-{self.year}")
            self.slug = base_slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """
        تولید URL مطلق برای این آبجکت
        استفاده در ادمین و redirect
        """
        return reverse('cars:car_detail', kwargs={
            'pk': self.pk, 
            'slug': self.slug
        })
    
    def get_main_image(self):
        """دریافت تصویر اصلی خودرو"""
        return self.images.filter(is_main=True).first()
    
    def get_all_images(self):
        """دریافت تمام تصاویر خودرو"""
        return self.images.all()
    
    def is_favorited_by(self, user):
        """بررسی آیا کاربر این خودرو را به علاقه‌مندی‌ها اضافه کرده"""
        if not user.is_authenticated:
            return False
        return self.favorited_by.filter(user=user).exists()
    
    # 🔹 **متدهای کمکی برای نمایش مقادیر**
    
    def get_color_display(self):
        """نمایش فارسی رنگ"""
        return dict(self.COLOR_CHOICES).get(self.color, self.color)
    
    def get_transmission_display(self):
        """نمایش فارسی گیربکس"""
        return dict(self.TRANSMISSION_CHOICES).get(self.transmission, self.transmission)
    
    def get_fuel_type_display(self):
        """نمایش فارسی نوع سوخت"""
        return dict(self.FUEL_CHOICES).get(self.fuel_type, self.fuel_type)
    
    def get_condition_display(self):
        """نمایش فارسی وضعیت بدنه"""
        return dict(self.CONDITION_CHOICES).get(self.condition, self.condition)

        
class CarImage(models.Model):
    """
    مدل تصاویر خودرو
    رابطه چند به یک با مدل Car
    """
    car = models.ForeignKey(
        Car, 
        on_delete=models.CASCADE,  # اگر خودرو حذف شد، تصاویرش هم حذف شوند
        related_name='images'  # دسترسی از طریق car.images
    )
    
    image = models.ImageField(
        upload_to='cars/images/%Y/%m/%d/',  # ساختار پوشه بر اساس تاریخ
        verbose_name='تصویر'
    )
    
    is_main = models.BooleanField(
        default=False, 
        verbose_name='تصویر اصلی'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='تاریخ آپلود'
    )
    
    class Meta:
        verbose_name = 'تصویر خودرو'
        verbose_name_plural = 'تصاویر خودرو'
        ordering = ['-is_main', 'uploaded_at']  # تصویر اصلی اول
    
    def __str__(self):
        return f"تصویر {self.car.title}"
    
    def save(self, *args, **kwargs):
        """ذخیره با تنظیم تصویر اصلی"""
        # اگر این تصویر اصلی است
        if self.is_main:
            # تمام تصاویر دیگر این خودرو را غیر اصلی کن
            CarImage.objects.filter(car=self.car).exclude(id=self.id).update(is_main=False)
        super().save(*args, **kwargs)
class Favorite(models.Model):
    """
    مدل علاقه‌مندی‌ها
    رابطه چند به چند بین User و Car
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    
    car = models.ForeignKey(
        Car, 
        on_delete=models.CASCADE, 
        related_name='favorited_by'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'علاقه‌مندی‌ها'
        unique_together = ['user', 'car']  # جلوگیری از duplicate
    
    def __str__(self):
        return f"{self.user.username} - {self.car.title}"
class Comment(models.Model):
    """مدل نظرات برای خودروها"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='car_comments')
    text = models.TextField(verbose_name='نظر')
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name='امتیاز'
    )
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"نظر {self.user.username} برای {self.car.title}"
class Comparison(models.Model):
    """مدل مقایسه خودروها"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    cars = models.ManyToManyField(Car, related_name='in_comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'مقایسه'
        verbose_name_plural = 'مقایسه‌ها'
    
    def __str__(self):
        return f"مقایسه {self.user.username}"

