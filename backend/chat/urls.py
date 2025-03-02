from django.urls import path
from .views import chat, send_message, create_chat

urlpatterns = [
    path('', chat, name='chat'),
    path('send_message/', send_message, name='send_message'),
    path('create_chat/', create_chat, name='create_rag'),
]