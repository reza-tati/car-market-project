# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        has_access = await self.check_room_access(self.room_id, self.user)
        if not has_access:
            await self.close(code=4003)
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        messages = await self.get_old_messages(self.room_id)
        await self.send(text_data=json.dumps({
            'type': 'old_messages',
            'messages': messages
        }))
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'user_id': self.user.id,
                    'is_typing': False,
                }
            )
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            # ✅ پیام متنی
            if message_type == 'message':
                message_text = data.get('message', '').strip()
                
                if not message_text:
                    return
                
                message = await self.save_message(
                    self.room_id,
                    self.user,
                    text=message_text
                )
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message_text,
                        'image_url': None,
                        'sender_id': self.user.id,
                        'sender_username': self.user.username,
                        'timestamp': message['timestamp'],
                    }
                )
            
            # ✅ پیام عکس‌دار
            elif message_type == 'image_message':
                image_url = data.get('image_url', '')
                caption = data.get('caption', '').strip()
                
                if not image_url:
                    return
                
                message = await self.save_message(
                    self.room_id,
                    self.user,
                    text=caption if caption else None,
                    image_path=image_url
                )
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': caption,
                        'image_url': message['image_url'],
                        'sender_id': self.user.id,
                        'sender_username': self.user.username,
                        'timestamp': message['timestamp'],
                    }
                )
            
            # ✅ وضعیت تایپ
            elif message_type == 'typing':
                is_typing = data.get('is_typing', False)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_status',
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'is_typing': is_typing,
                    }
                )
        
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event.get('message', ''),
            'image_url': event.get('image_url'),
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
        }))
    
    async def typing_status(self, event):
        if event.get('user_id') == self.user.id:
            return
        
        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'user_id': event.get('user_id'),
            'username': event.get('username', ''),
            'is_typing': event.get('is_typing', False),
        }))
    
    @database_sync_to_async
    def check_room_access(self, room_id, user):
        try:
            room = ChatRoom.objects.get(id=room_id)
            return room.user1 == user or room.user2 == user
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_old_messages(self, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            messages = room.messages.all().order_by('timestamp')[:50]
            room.messages.filter(is_read=False).exclude(sender=self.user).update(is_read=True)
            
            return [
                {
                    'id': msg.id,
                    'text': msg.text or '',
                    'image_url': msg.image.url if msg.image else None,
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
    def save_message(self, room_id, sender, text=None, image_path=None):
        room = ChatRoom.objects.get(id=room_id)
        message = Message.objects.create(
            room=room,
            sender=sender,
            text=text,
            image=image_path
        )
        room.save()
        
        return {
            'id': message.id,
            'text': message.text,
            'image_url': message.image.url if message.image else None,
            'timestamp': message.timestamp.strftime('%H:%M'),
        }