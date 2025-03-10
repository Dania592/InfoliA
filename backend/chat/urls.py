from django.urls import path
from .views import  send_message, create_chat, load_chat, FileUploadView, get_user_chats, add_file

urlpatterns = [
    path('send_message/', send_message, name='send_message'),
    path('create_chat/', create_chat, name='create_chat'),
    path('load_chat/', load_chat, name='load_chat'),
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path('add_file/', add_file, name='add_file'),
    path("get_user_chats/", get_user_chats, name="get_user_chats"),
]