# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer برای مدیریت WebSocket چت
    """
    
    async def connect(self):
        """اتصال WebSocket"""
        self.user = self.scope['user']
        
        # اگه کاربر لاگین نکرده، رد کن
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # دریافت room_id از URL
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # بررسی دسترسی به اتاق
        has_access = await self.check_room_access(self.room_id, self.user)
        if not has_access:
            await self.close()
            return
        
        # اضافه کردن به گروه
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # ارسال پیام‌های قدیمی
        messages = await self.get_old_messages(self.room_id)
        await self.send(text_data=json.dumps({
            'type': 'old_messages',
            'messages': messages
        }))
    
    async def disconnect(self, close_code):
        """قطع اتصال WebSocket"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """دریافت پیام از WebSocket"""
        try:
            data = json.loads(text_data)
            message_text = data.get('message', '').strip()
            
            if not message_text:
                return
            
            # ذخیره پیام در دیتابیس
            message = await self.save_message(
                self.room_id,
                self.user,
                message_text
            )
            
            # ارسال به گروه
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'timestamp': message['timestamp'],
                }
            )
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        """ارسال پیام به WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
        }))
    
    @database_sync_to_async
    def check_room_access(self, room_id, user):
        """بررسی دسترسی کاربر به اتاق چت"""
        try:
            room = ChatRoom.objects.get(id=room_id)
            return room.user1 == user or room.user2 == user
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_old_messages(self, room_id):
        """دریافت پیام‌های قدیمی"""
        try:
            room = ChatRoom.objects.get(id=room_id)
            messages = room.messages.all().order_by('timestamp')[:50]
            
            # علامت‌گذاری پیام‌ها به عنوان خوانده شده
            room.messages.filter(is_read=False).exclude(sender=self.user).update(is_read=True)
            
            return [
                {
                    'id': msg.id,
                    'text': msg.text,
                    'sender_id': msg.sender.id,
                    'sender_username': msg.sender.username,
                    'timestamp': msg.timestamp.strftime('%H:%M'),
                    'is_read': msg.is_read,
                }
                for msg in messages
            ]
        except ChatRoom.DoesNotExist:
            return []
    
    @database_sync_to_async
    def save_message(self, room_id, sender, text):
        """ذخیره پیام در دیتابیس"""
        room = ChatRoom.objects.get(id=room_id)
        message = Message.objects.create(
            room=room,
            sender=sender,
            text=text
        )
        
        # بروزرسانی زمان اتاق
        room.save()
        
        return {
            'id': message.id,
            'text': message.text,
            'timestamp': message.timestamp.strftime('%H:%M'),
        }