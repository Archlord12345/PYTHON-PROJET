from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    requested_role = request.GET.get('role', 'Caissier')
    if request.method == 'POST':
        login_val = request.POST.get('login')
        password = request.POST.get('password')
        
        # Django authenticate uses the field defined in USERNAME_FIELD
        user = authenticate(request, login=login_val, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect based on role if needed, or just to home/dashboard
            if user.role == 'Caissier':
                return redirect('caisse:index')
            else:
                return redirect('articles:liste_articles')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
    
    context = {
        'role': requested_role,
        'title': f"Connexion - {requested_role}"
    }
    return render(request, 'authentification/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')
