from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, MessageSerializer
from .models import Message
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.exceptions import ValidationError



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت شده می‌توانند پیام ارسال کنند

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageListView(APIView):
    def get(self, request, sender_id, receiver_id):
        messages = Message.objects.filter(sender_id=sender_id, receiver_id=receiver_id) | \
                   Message.objects.filter(sender_id=receiver_id, receiver_id=sender_id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        if 'file' in request.FILES:
            if request.FILES['file'].size > 104857600:  # 100 مگابایت
                return Response({"error": "File size exceeds 100MB limit"}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    