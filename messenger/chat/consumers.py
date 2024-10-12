import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from channels.db import database_sync_to_async
from yourapp.models import Message  # مطمئن شوید که مدل Message شما اینجا وارد شده است
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
            await self.save_message(message)  # ذخیره پیام در دیتابیس
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

            # ذخیره تصویر در دیتابیس
            image_url = await self.save_image(image)

            # ارسال پیام تصویری
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_image',
                    'image': image_url
                }
            )

        # ذخیره فایل صوتی اگر وجود داشته باشد
        if audio_data:
            audio_data = base64.b64decode(audio_data)
            audio = ContentFile(audio_data, name='chat_audio.mp3')

            # ذخیره فایل صوتی در دیتابیس
            audio_url = await self.save_audio(audio)

            # ارسال پیام صوتی
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_audio',
                    'audio': audio_url
                }
            )

    # ذخیره پیام در دیتابیس
    @database_sync_to_async
    def save_message(self, message):
        Message.objects.create(content=message, sender=self.scope['user'])

    # ذخیره تصویر در دیتابیس
    @database_sync_to_async
    def save_image(self, image):
        # باید اینجا مدل خود را ایجاد کنید و تصویر را ذخیره کنید
        # مثلا:
        # image_instance = ImageModel(image=image)
        # image_instance.save()
        return '/media/chat_image.png'  # برگرداندن URL واقعی تصویر

        # ذخیره فایل صوتی در دیتابیس
    @database_sync_to_async
    def save_audio(self, audio):
        # مشابه با save_image
        return '/media/chat_audio.mp3'  # برگرداندن URL واقعی فایل صوتی

    # دریافت پیام متنی از گروه چت
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # دریافت تصویر از گروه چت
    async def chat_image(self, event):
        image = event['image']
        await self.send(text_data=json.dumps({
            'image': image
        }))

    # دریافت فایل صوتی از گروه چت
    async def chat_audio(self, event):
        audio = event['audio']
        await self.send(text_data=json.dumps({
            'audio': audio
        }))