from django.urls import path
from .views import  send_message, create_chat, FileUploadView, get_user_chats

urlpatterns = [
    path('send_message/', send_message, name='send_message'),
    path('create_chat/', create_chat, name='create_chat'),
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("get_user_chats/", get_user_chats, name="get_user_chats"),
]