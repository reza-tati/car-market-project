# carmarket/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from azbankgateways.urls import az_bank_gateways_urls
from django.views.generic import TemplateView
from cars.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bankgateways/', az_bank_gateways_urls()),
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('search/', include('search.urls', namespace='search')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('cars/', include('cars.urls')),
    # API
    path('api/', include('cars.api_urls')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)