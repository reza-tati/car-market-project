# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('start/<str:vehicle_type>/<int:vehicle_id>/', views.start_chat, name='start_chat'),
]