# cars/api.py (ایجاد فایل جدید)
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Car, Brand, CarModel, CarImage, Favorite
from .serializers import (
    CarSerializer, CarListSerializer, BrandSerializer, 
    CarModelSerializer, CarImageSerializer
)

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CarModelViewSet(viewsets.ModelViewSet):
    queryset = CarModel.objects.all()
    serializer_class = CarModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['brand']

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.filter(is_active=True, is_verified=True)
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'model', 'city', 'transmission', 'fuel_type', 'year']
    search_fields = ['title', 'description', 'brand__name', 'model__name']
    ordering_fields = ['price', 'year', 'mileage', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CarListSerializer
        return CarSerializer
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        car = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response({'error': 'نیاز به ورود'}, status=status.HTTP_401_UNAUTHORIZED)
        
        favorite, created = Favorite.objects.get_or_create(user=user, car=car)
        
        if not created:
            favorite.delete()
            return Response({'status': 'removed', 'message': 'از علاقه‌مندی‌ها حذف شد'})
        
        return Response({'status': 'added', 'message': 'به علاقه‌مندی‌ها اضافه شد'})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_cars = self.get_queryset().filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured_cars, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_cars(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'نیاز به ورود'}, status=status.HTTP_401_UNAUTHORIZED)
        
        my_cars = Car.objects.filter(seller=request.user)
        serializer = self.get_serializer(my_cars, many=True)
        return Response(serializer.data)

class CarImageViewSet(viewsets.ModelViewSet):
    queryset = CarImage.objects.all()
    serializer_class = CarImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]