from django.urls import path
from .views import RegisterView, MessageCreateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('messages/send/', MessageCreateView.as_view(), name='send-message'),
]
