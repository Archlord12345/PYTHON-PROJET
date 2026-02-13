from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def gestionnaire_required(view_func):
    """
    Décorateur qui restreint l'accès aux gestionnaires et administrateurs.
    Les caissiers sont redirigés vers la caisse.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentification:login')
        
        # Vérifier si l'utilisateur est un gestionnaire ou administrateur
        if request.user.role in ['Gestionnaire', 'Administrateur', 'Comptable']:
            return view_func(request, *args, **kwargs)
        
        # Si c'est un caissier, rediriger vers la caisse
        if request.user.role == 'Caissier':
            messages.warning(request, "Accès réservé aux gestionnaires.")
            return redirect('caisse:index')
        
        # Par défaut, rediriger vers la caisse
        return redirect('caisse:index')
    
    return _wrapped_view


def admin_required(view_func):
    """
    Décorateur qui restreint l'accès uniquement aux administrateurs.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentification:login')
        
        # Vérifier si l'utilisateur est un administrateur
        if request.user.role == 'Administrateur':
            return view_func(request, *args, **kwargs)
        
        # Sinon, message d'erreur et redirection
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('gestionnaire:dashboard')
    
    return _wrapped_view


def caissier_or_gestionnaire(view_func):
    """
    Décorateur qui permet l'accès aux caissiers et gestionnaires.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentification:login')
        
        # Tous les rôles authentifiés ont accès
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
