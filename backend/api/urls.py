from django.urls import path
from .views import register
from .views import login

urlpatterns = [
    path('register/', register, name="inscription"),
    path('login/', login, name="connexion"),
]
