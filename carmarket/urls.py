# carmarket/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cars.urls', namespace='cars')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('search/', include('search.urls', namespace='search')),
    
    # API
    path('api/', include('cars.api_urls')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)