# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from .models import ChatRoom, Message


@login_required
def chat_list(request):
    """
    لیست همه چت‌های کاربر
    """
    # اتاق‌هایی که کاربر توشون هست
    chat_rooms = ChatRoom.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).order_by('-updated_at')
    
    # اضافه کردن اطلاعات هر اتاق
    rooms_data = []
    for room in chat_rooms:
        other_user = room.get_other_user(request.user)
        last_message = room.get_last_message()
        unread_count = room.get_unread_count(request.user)
        
        rooms_data.append({
            'room': room,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    context = {
        'rooms_data': rooms_data,
        'total_chats': chat_rooms.count(),
    }
    
    return render(request, 'chat/chat_list.html', context)


@login_required
def chat_room(request, room_id):
    """
    صفحه چت خصوصی
    """
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # بررسی دسترسی
    if request.user != room.user1 and request.user != room.user2:
        messages.error(request, 'شما به این چت دسترسی ندارید.')
        return redirect('chat:chat_list')
    
    # علامت‌گذاری پیام‌های خوانده نشده
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    other_user = room.get_other_user(request.user)
    
    context = {
        'room': room,
        'other_user': other_user,
        'messages': room.messages.all().order_by('timestamp'),
    }
    
    return render(request, 'chat/chat_room.html', context)


@login_required
def start_chat(request, vehicle_type, vehicle_id):
    """
    شروع چت جدید بین خریدار و فروشنده
    """
    from cars.models import Car, Motorcycle, HeavyVehicle
    
    # دریافت وسیله نقلیه
    if vehicle_type == 'car':
        vehicle = get_object_or_404(Car, id=vehicle_id)
    elif vehicle_type == 'motorcycle':
        vehicle = get_object_or_404(Motorcycle, id=vehicle_id)
    elif vehicle_type == 'heavy':
        vehicle = get_object_or_404(HeavyVehicle, id=vehicle_id)
    else:
        messages.error(request, 'نوع وسیله نقلیه نامعتبر است.')
        return redirect('cars:car_list')
    
    seller = vehicle.seller
    
    # اگه کاربر خودش فروشنده هست، نمی‌تونه با خودش چت کنه
    if request.user == seller:
        messages.warning(request, 'شما نمی‌توانید با خودتان چت کنید.')
        return redirect('cars:car_detail', pk=vehicle.pk, slug=vehicle.slug)
    
    # چک کن که اتاق چت قبلاً وجود داره یا نه
    room = ChatRoom.objects.filter(
        Q(user1=request.user, user2=seller) | Q(user1=seller, user2=request.user),
        vehicle_type=vehicle_type,
        vehicle_id=vehicle_id
    ).first()
    
    # اگه وجود نداشت، بساز
    if not room:
        room = ChatRoom.objects.create(
            user1=request.user,
            user2=seller,
            vehicle_type=vehicle_type,
            vehicle_id=vehicle_id
        )
        messages.success(request, 'چت جدید ایجاد شد!')
    
    return redirect('chat:chat_room', room_id=room.id)