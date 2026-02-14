from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def _redirect_after_login(user):
    role = getattr(user, "role", "")
    if role == "Caissier":
        return redirect("caisse:index")
    return redirect("gestionnaire:dashboard")

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_after_login(request.user)

    if request.method == 'POST':
        login_val = request.POST.get('login')
        password = request.POST.get('password')
        
        # Django authenticate uses the field defined in USERNAME_FIELD
        user = authenticate(request, login=login_val, password=password)
        
        if user is not None:
            if not user.is_active:
                messages.error(request, "Compte desactive. Contactez un gestionnaire.")
                return redirect("authentification:login")
            login(request, user)
            return _redirect_after_login(user)
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
    
    context = {
        'title': "Connexion"
    }
    return render(request, 'authentification/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')
