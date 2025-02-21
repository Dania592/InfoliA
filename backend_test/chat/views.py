from django.shortcuts import render

# Create your views here.
def chat(request):
    return render(request, 'chat.html')

def home(request):
    return render(request, 'home.html')