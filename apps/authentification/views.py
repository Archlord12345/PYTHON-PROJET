from django.shortcuts import render

def login_view(request):
    return render(request, 'authentification/login.html')

def signup_view(request):
    return render(request, 'authentification/signup.html')
