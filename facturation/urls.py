"""
URL configuration for facturation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from apps.authentification import views

# Vue pour la page d'accueil
def home_view(request):
    return render(request, 'home.html')

# vue pour la sélection du profil de connexion
def selection_profil_view(request):
    return render(request, 'selection_profil.html')

# Importer les vues de l'application d'authentification
def client_signup(request):
    return render(request, 'authentification/client_signup.html')
# Vue pour la page de connexion du client
def client_signin(request):
    return render(request, 'authentification/client_signin.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    # =======================================================================
    path('selection-profil/', selection_profil_view, name='selection_profil'),
    path('client/inscription/', views.client_signup, name='client_signup'),
    path('client/connexion/', views.client_signin, name='client_signin'),

    # Tailwind development server
    path("__reload__/", include("django_browser_reload.urls")),
    
    # Apps urls
    path('audit_journal/', include('apps.audit_journal.urls')),
    path('checkout/', include('apps.checkout.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('handle_articles/', include('apps.handle_articles.urls')),
    path('handle_customers/', include('apps.handle_customers.urls')),
    path('handle_users/', include('apps.handle_users.urls')),
    path('report/', include('apps.report.urls')),
    path('settings/', include('apps.settings.urls')),
]
