# payments/urls.py
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('start/<str:vehicle_type>/<int:vehicle_id>/', views.start_payment, name='start_payment'),
    path('callback/', views.payment_callback, name='callback'),
    path('history/', views.payment_history, name='payment_history'),
]