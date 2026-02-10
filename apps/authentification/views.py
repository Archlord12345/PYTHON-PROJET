from django.shortcuts import render

def login_view(request):
    return render(request, 'authentification/login.html')

def signup_view(request):
    return render(request, 'authentification/signup.html')

def client_signup(request):
    return render(request, 'authentification/client_signup.html')

def client_signin(request):
    return render(request, 'authentification/client_signin.html')