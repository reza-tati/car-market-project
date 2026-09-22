# chat/context_processors.py
from django.db.models import Q
from .models import ChatRoom, Message


def unread_messages_count(request):
    """
    تعداد پیام‌های خونده نشده کاربر در همه اتاق‌ها
    """
    if not request.user.is_authenticated:
        return {'unread_messages_count': 0}
    
    # اتاق‌های کاربر
    user_rooms = ChatRoom.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )
    
    # پیام‌های خونده نشده که کاربر فرستنده‌شون نبوده
    count = Message.objects.filter(
        room__in=user_rooms,
        is_read=False
    ).exclude(
        sender=request.user
    ).count()
    
    return {'unread_messages_count': count}