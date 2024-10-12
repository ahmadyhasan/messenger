from django.urls import path
from .views import RegisterView, MessageCreateView, MessageListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('messages/send/', MessageCreateView.as_view(), name='send-message'),
    path('<int:sender_id>/<int:receiver_id>/', MessageListView.as_view(), name='message-list'),
    path('send/', MessageListView.as_view(), name='send-message'),
]
