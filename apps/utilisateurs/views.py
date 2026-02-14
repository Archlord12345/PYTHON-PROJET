from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from facturation.models import Utilisateur
from apps.gestionnaire.decorators import gestionnaire_required


@login_required
@gestionnaire_required
def index(request):
    """Liste tous les utilisateurs"""
    utilisateurs = Utilisateur.objects.all().order_by('role', 'login')
    
    # Rôles disponibles pour création
    role_choices = [
        ('Caissier', 'Caissier'),
        ('Gestionnaire', 'Gestionnaire'),
    ]
    
    context = {
        'utilisateurs': utilisateurs,
        'role_choices': role_choices,
        'total_utilisateurs': utilisateurs.count(),
        'total_caissiers': utilisateurs.filter(role='Caissier').count(),
        'total_gestionnaires': utilisateurs.filter(role='Gestionnaire').count(),
    }
    return render(request, 'utilisateurs/index.html', context)


@login_required
@gestionnaire_required
def create_user(request):
    """Créer un nouvel utilisateur"""
    if request.method != 'POST':
        return redirect('utilisateurs:index')
    
    login = request.POST.get('login', '').strip()
    password = request.POST.get('password', '').strip()
    role = request.POST.get('role', 'Caissier')
    
    if not login or not password:
        messages.error(request, "Le login et le mot de passe sont requis.")
        return redirect('utilisateurs:index')
    
    if role not in ['Caissier', 'Gestionnaire']:
        messages.error(request, "Rôle invalide.")
        return redirect('utilisateurs:index')
    
    try:
        user = Utilisateur.objects.create(
            login=login,
            role=role,
        )
        user.set_password(password)
        user.save()
        messages.success(request, f"Utilisateur '{login}' créé avec succès.")
    except IntegrityError:
        messages.error(request, f"Le login '{login}' est déjà utilisé.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la création : {str(e)}")
    
    return redirect('utilisateurs:index')


@login_required
@gestionnaire_required
def update_user(request, user_id):
    """Modifier un utilisateur existant"""
    if request.method != 'POST':
        return redirect('utilisateurs:index')
    
    user = get_object_or_404(Utilisateur, id=user_id)
    
    login = request.POST.get('login', '').strip()
    role = request.POST.get('role', user.role)
    password = request.POST.get('password', '').strip()
    is_active = request.POST.get('is_active') == 'on'
    
    if not login:
        messages.error(request, "Le login est requis.")
        return redirect('utilisateurs:index')
    
    try:
        # Vérifier si le nouveau login n'est pas déjà pris par un autre user
        if login != user.login and Utilisateur.objects.filter(login=login).exists():
            messages.error(request, f"Le login '{login}' est déjà utilisé.")
            return redirect('utilisateurs:index')
        
        user.login = login
        user.role = role
        user.is_active = is_active
        
        # Ne changer le mot de passe que si fourni
        if password:
            user.set_password(password)
        
        user.save()
        messages.success(request, f"Utilisateur '{login}' mis à jour avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la mise à jour : {str(e)}")
    
    return redirect('utilisateurs:index')


@login_required
@gestionnaire_required
def delete_user(request, user_id):
    """Supprimer un utilisateur"""
    if request.method != 'POST':
        return redirect('utilisateurs:index')
    
    user = get_object_or_404(Utilisateur, id=user_id)
    
    # Empêcher la suppression de son propre compte
    if user.id == request.user.id:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('utilisateurs:index')
    
    try:
        login = user.login
        user.delete()
        messages.success(request, f"Utilisateur '{login}' supprimé avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    
    return redirect('utilisateurs:index')
