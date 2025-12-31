# cars/serializers.py (ایجاد فایل جدید)
from rest_framework import serializers
from .models import Car, Brand, CarModel, CarImage
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'country', 'logo']

class CarModelSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), 
        source='brand', 
        write_only=True
    )
    
    class Meta:
        model = CarModel
        fields = ['id', 'name', 'brand', 'brand_id', 'production_years', 'category']

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image', 'is_main', 'uploaded_at']

class CarSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    model = CarModelSerializer(read_only=True)
    images = CarImageSerializer(many=True, read_only=True)
    
    # فیلدهای write-only
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), 
        source='brand', 
        write_only=True
    )
    model_id = serializers.PrimaryKeyRelatedField(
        queryset=CarModel.objects.all(), 
        source='model', 
        write_only=True
    )
    
    class Meta:
        model = Car
        fields = [
            'id', 'title', 'slug', 'seller', 'brand', 'model', 'brand_id', 'model_id',
            'year', 'price', 'mileage', 'color', 'transmission', 'fuel_type',
            'engine_capacity', 'engine_power', 'condition', 'has_insurance',
            'insurance_expiry', 'has_service_book', 'description', 'city',
            'district', 'address', 'is_sold', 'is_active', 'is_verified',
            'is_featured', 'views', 'phone_views', 'created_at', 'updated_at',
            'images'
        ]
        read_only_fields = ['slug', 'views', 'phone_views', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # تنظیم فروشنده به کاربر جاری
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

class CarListSerializer(serializers.ModelSerializer):
    """Serializer مختصر برای لیست خودروها"""
    brand_name = serializers.CharField(source='brand.name')
    model_name = serializers.CharField(source='model.name')
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Car
        fields = [
            'id', 'title', 'slug', 'brand_name', 'model_name', 'year', 'price',
            'mileage', 'city', 'is_featured', 'views', 'created_at', 'main_image'
        ]
    
    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return self.context['request'].build_absolute_uri(main_image.image.url)
        return None