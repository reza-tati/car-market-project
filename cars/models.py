# cars/models.py
from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify


# ============================================
# مدل‌های کمکی (برند و مدل)
# ============================================

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='نام برند')
    logo = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name='کشور سازنده')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'
        ordering = ['name']

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models', verbose_name='برند')
    name = models.CharField(max_length=100, verbose_name='نام مدل')
    production_years = models.CharField(max_length=50, verbose_name='سال‌های تولید')

    CATEGORY_CHOICES = [
        ('sedan', 'سدان'),
        ('hatchback', 'هاچ‌بک'),
        ('suv', 'شاسی‌بلند'),
        ('pickup', 'وانت'),
        ('coupe', 'کوپه'),
        ('convertible', 'کروک'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='sedan', verbose_name='دسته‌بندی')

    class Meta:
        verbose_name = 'مدل خودرو'
        verbose_name_plural = 'مدل خودروها'
        ordering = ['brand', 'name']
        unique_together = ['brand', 'name']

    def __str__(self):
        return f"{self.brand.name} {self.name}"


# ============================================
# مدل‌های اصلی (سواری، موتورسیکلت، سنگین)
# ============================================

class BaseVehicle(models.Model):
    """مدل پایه برای همه وسایل نقلیه (abstract)"""
    
    VEHICLE_TYPE_CHOICES = [
        ('car', 'سواری'),
        ('motorcycle', 'موتورسیکلت'),
        ('heavy', 'ماشین سنگین'),
    ]

    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='car', verbose_name='نوع وسیله نقلیه')
    
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_vehicles',  # ← این مشکل related_name رو حل میکنه
        verbose_name='فروشنده'
    )
    
    title = models.CharField(max_length=200, verbose_name='عنوان آگهی')
    slug = models.SlugField(max_length=250, unique_for_date='created_at', blank=True)
    
    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='قیمت (تومان)')
    city = models.CharField(max_length=100, verbose_name='شهر')
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name='منطقه')
    address = models.TextField(blank=True, null=True, verbose_name='آدرس دقیق')
    description = models.TextField(verbose_name='توضیحات')
    
    is_sold = models.BooleanField(default=False, verbose_name='فروخته شده')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    is_featured = models.BooleanField(default=False, verbose_name='آگهی ویژه')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    views = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    phone_views = models.PositiveIntegerField(default=0, verbose_name='تعداد نمایش شماره')

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            
            # اگه slugify خالی برگردوند (متن فارسی)، از UUID استفاده کن
            if not base_slug:
                import uuid
                base_slug = str(uuid.uuid4())[:8]
            
            self.slug = base_slug
        
        super().save(*args, **kwargs)

    

# ============================================
# مدل سواری (Car)
# ============================================

class Car(BaseVehicle):
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, verbose_name='برند')
    model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True, verbose_name='مدل')
    year = models.PositiveIntegerField(verbose_name='سال ساخت')
    mileage = models.PositiveIntegerField(verbose_name='کارکرد (کیلومتر)')

    COLOR_CHOICES = [
        ('white', 'سفید'), ('black', 'مشکی'), ('silver', 'نقره‌ای'),
        ('gray', 'خاکستری'), ('red', 'قرمز'), ('blue', 'آبی'),
        ('green', 'سبز'), ('brown', 'قهوه‌ای'), ('yellow', 'زرد'),
    ]
    color = models.CharField(max_length=50, choices=COLOR_CHOICES, verbose_name='رنگ')

    TRANSMISSION_CHOICES = [
        ('manual', 'دستی'),
        ('automatic', 'اتوماتیک'),
        ('cvt', 'CVT'),
        ('dual_clutch', 'دوکلاچه'),
    ]
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, verbose_name='گیربکس')

    FUEL_CHOICES = [
        ('petrol', 'بنزینی'),
        ('diesel', 'دیزل'),
        ('hybrid', 'هیبرید'),
        ('electric', 'الکتریکی'),
        ('cng', 'گازسوز'),
    ]
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, verbose_name='نوع سوخت')

    engine_capacity = models.PositiveIntegerField(verbose_name='حجم موتور (سی‌سی)')
    engine_power = models.PositiveIntegerField(blank=True, null=True, verbose_name='قدرت موتور (اسب)')

    CONDITION_CHOICES = [
        ('excellent', 'عالی'),
        ('good', 'خوب'),
        ('average', 'متوسط'),
        ('damaged', 'آسیب‌دیده'),
        ('accident', 'تصادفی'),
    ]
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, verbose_name='وضعیت بدنه')

    has_insurance = models.BooleanField(default=False, verbose_name='بیمه دارد')
    insurance_expiry = models.DateField(blank=True, null=True, verbose_name='تاریخ انقضای بیمه')
    has_service_book = models.BooleanField(default=False, verbose_name='دفترچه سرویس دارد')

    class Meta:
        verbose_name = 'سواری'
        verbose_name_plural = 'سواری‌ها'
    def get_absolute_url(self):
        return reverse('cars:car_detail', kwargs={'pk': self.pk, 'slug': self.slug})

# ============================================
# مدل موتورسیکلت (Motorcycle)
# ============================================

class Motorcycle(BaseVehicle):
    MOTORCYCLE_BRAND_CHOICES = [
        ('honda', 'هوندا'),
        ('yamaha', 'یاماها'),
        ('suzuki', 'سوزوکی'),
        ('kawasaki', 'کاوازاکی'),
        ('bmw', 'بی‌ام‌و'),
        ('ducati', 'دوکاتی'),
        ('harley', 'هارلی'),
        ('iranian', 'ایرانی'),
    ]

    brand = models.CharField(max_length=50, choices=MOTORCYCLE_BRAND_CHOICES, verbose_name='برند')
    model_name = models.CharField(max_length=100, verbose_name='مدل')
    year = models.PositiveIntegerField(verbose_name='سال ساخت')
    mileage = models.PositiveIntegerField(verbose_name='کارکرد (کیلومتر)')
    engine_cc = models.PositiveIntegerField(verbose_name='حجم موتور (سی‌سی)')

    COLOR_CHOICES = [
        ('white', 'سفید'), ('black', 'مشکی'), ('silver', 'نقره‌ای'),
        ('gray', 'خاکستری'), ('red', 'قرمز'), ('blue', 'آبی'),
        ('green', 'سبز'), ('yellow', 'زرد'),
    ]
    color = models.CharField(max_length=50, choices=COLOR_CHOICES, verbose_name='رنگ')

    has_abs = models.BooleanField(default=False, verbose_name='ABS دارد')
    has_helmet_box = models.BooleanField(default=False, verbose_name='محفظه کلاه دارد')
    is_imported = models.BooleanField(default=False, verbose_name='وارداتی')

    class Meta:
        verbose_name = 'موتورسیکلت'
        verbose_name_plural = 'موتورسیکلت‌ها'
    def get_absolute_url(self):
        return reverse('cars:motorcycle_detail', kwargs={'pk': self.pk, 'slug': self.slug})

# ============================================
# مدل ماشین سنگین (HeavyVehicle)
# ============================================

class HeavyVehicle(BaseVehicle):
    HEAVY_TYPE_CHOICES = [
        ('truck', 'کامیون'),
        ('bus', 'اتوبوس'),
        ('trailer', 'تریلر'),
        ('loader', 'لودر'),
        ('crane', 'جرثقیل'),
        ('tanker', 'تانکر'),
    ]

    heavy_type = models.CharField(max_length=50, choices=HEAVY_TYPE_CHOICES, verbose_name='نوع ماشین سنگین')
    brand = models.CharField(max_length=100, verbose_name='برند')
    model_name = models.CharField(max_length=100, verbose_name='مدل')
    year = models.PositiveIntegerField(verbose_name='سال ساخت')
    load_capacity = models.PositiveIntegerField(verbose_name='ظرفیت بار (تن)')
    has_crane = models.BooleanField(default=False, verbose_name='جرثقیل دارد')
    is_imported = models.BooleanField(default=False, verbose_name='وارداتی')

    class Meta:
        verbose_name = 'ماشین سنگین'
        verbose_name_plural = 'ماشین‌های سنگین'
    def get_absolute_url(self):
        return reverse('cars:heavy_detail', kwargs={'pk': self.pk, 'slug': self.slug})

# ============================================
# مدل تصاویر (برای همه وسایل نقلیه)
# ============================================

class VehicleImage(models.Model):
    """مدل تصاویر برای همه وسایل نقلیه"""
    vehicle_id = models.PositiveIntegerField(verbose_name='شناسه وسیله نقلیه')
    vehicle_type = models.CharField(max_length=20, choices=BaseVehicle.VEHICLE_TYPE_CHOICES, verbose_name='نوع وسیله نقلیه')
    
    image = models.ImageField(upload_to='vehicles/images/%Y/%m/%d/', verbose_name='تصویر')
    is_main = models.BooleanField(default=False, verbose_name='تصویر اصلی')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')

    class Meta:
        verbose_name = 'تصویر وسیله نقلیه'
        verbose_name_plural = 'تصاویر وسایل نقلیه'
        ordering = ['-is_main', 'uploaded_at']

    def __str__(self):
        return f"تصویر {self.vehicle_type} - {self.vehicle_id}"


# cars/models.py (بعد از مدل VehicleImage اضافه کن)

class CarImage(models.Model):
    """مدل تصاویر خودرو (سواری)"""
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='car_images',  # ← تغییر دادم به car_images
        verbose_name='خودرو'
    )
    
    image = models.ImageField(
        upload_to='cars/images/%Y/%m/%d/',
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
        ordering = ['-is_main', 'uploaded_at']
    
    def __str__(self):
        return f"تصویر {self.car.title}"
    
    def save(self, *args, **kwargs):
        if self.is_main:
            CarImage.objects.filter(car=self.car).exclude(id=self.id).update(is_main=False)
        super().save(*args, **kwargs)


class MotorcycleImage(models.Model):
    """مدل تصاویر موتورسیکلت"""
    motorcycle = models.ForeignKey(
        Motorcycle,
        on_delete=models.CASCADE,
        related_name='motorcycle_images',  # ← related_name متفاوت
        verbose_name='موتورسیکلت'
    )
    
    image = models.ImageField(
        upload_to='motorcycles/images/%Y/%m/%d/',
        verbose_name='تصویر'
    )
    
    is_main = models.BooleanField(default=False, verbose_name='تصویر اصلی')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    
    class Meta:
        verbose_name = 'تصویر موتورسیکلت'
        verbose_name_plural = 'تصاویر موتورسیکلت'
        ordering = ['-is_main', 'uploaded_at']
    
    def __str__(self):
        return f"تصویر {self.motorcycle.title}"
    
    def save(self, *args, **kwargs):
        if self.is_main:
            MotorcycleImage.objects.filter(motorcycle=self.motorcycle).exclude(id=self.id).update(is_main=False)
        super().save(*args, **kwargs)


class HeavyVehicleImage(models.Model):
    """مدل تصاویر ماشین سنگین"""
    heavy = models.ForeignKey(
        HeavyVehicle,
        on_delete=models.CASCADE,
        related_name='heavy_images',  # ← related_name متفاوت
        verbose_name='ماشین سنگین'
    )
    
    image = models.ImageField(
        upload_to='heavies/images/%Y/%m/%d/',
        verbose_name='تصویر'
    )
    
    is_main = models.BooleanField(default=False, verbose_name='تصویر اصلی')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    
    class Meta:
        verbose_name = 'تصویر ماشین سنگین'
        verbose_name_plural = 'تصاویر ماشین‌های سنگین'
        ordering = ['-is_main', 'uploaded_at']
    
    def __str__(self):
        return f"تصویر {self.heavy.title}"
    
    def save(self, *args, **kwargs):
        if self.is_main:
            HeavyVehicleImage.objects.filter(heavy=self.heavy).exclude(id=self.id).update(is_main=False)
        super().save(*args, **kwargs)

                
# ============================================
# مدل علاقه‌مندی (برای همه وسایل نقلیه)
# ============================================

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='کاربر')
    vehicle_id = models.PositiveIntegerField(verbose_name='شناسه وسیله نقلیه')
    vehicle_type = models.CharField(max_length=20, choices=BaseVehicle.VEHICLE_TYPE_CHOICES, verbose_name='نوع وسیله نقلیه')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ افزودن')

    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'علاقه‌مندی‌ها'
        unique_together = ['user', 'vehicle_id', 'vehicle_type']

    def __str__(self):
        return f"{self.user.username} - {self.vehicle_type} - {self.vehicle_id}"