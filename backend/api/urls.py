from django.urls import path
from .views import register
from .views import login
from rest_framework.decorators import api_view
urlpatterns = [
    path('register/', register, name="inscription"),
    path('login/', login, name="connexion"),
]
