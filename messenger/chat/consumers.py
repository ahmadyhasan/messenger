import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
import base64

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['user'].username  # به جای اتاق گروهی، هر کاربر اتاق خودش را دارد
        self.room_group_name = f'chat_{self.room_name}'

        # پیوستن به گروه چت
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # ترک گروه چت
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # دریافت پیام از WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        image_data = text_data_json.get('image', None)
        audio_data = text_data_json.get('audio', None)
        
        # ذخیره پیام متنی
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )
        
        # ذخیره تصویر اگر وجود داشته باشد
        if image_data:
            image_data = base64.b64decode(image_data)
            image = ContentFile(image_data, name='chat_image.png')

            # ارسال پیام تصویری
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_image',
                    'image': image
                }
            )

        # ذخیره فایل صوتی اگر وجود داشته باشد
        if audio_data:
            audio_data = base64.b64decode(audio_data)
            audio = ContentFile(audio_data, name='chat_audio.mp3')

            # ارسال پیام صوتی
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_audio',
                    'audio': audio
                }
            )

    # دریافت پیام متنی از گروه چت
    async def chat_message(self, event):
        message = event['message']

        # ارسال پیام به WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # دریافت تصویر از گروه چت
    async def chat_image(self, event):
        image = event['image']

        # ارسال تصویر به WebSocket
        await self.send(text_data=json.dumps({
            'image': image.url
        }))

    # دریافت فایل صوتی از گروه چت
    async def chat_audio(self, event):
        audio = event['audio']

        # ارسال فایل صوتی به WebSocket
        await self.send(text_data=json.dumps({
            'audio': audio.url
        }))
