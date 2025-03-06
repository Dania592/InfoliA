from django.urls import path
from .views import  send_message, create_chat, load_chat, FileUploadView

urlpatterns = [
    path('send_message/', send_message, name='send_message'),
    path('create_chat/', create_chat, name='create_chat'),
    path('load_chat/', load_chat, name='load_chat'),
    path("upload/", FileUploadView.as_view(), name="file-upload"),
]