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
from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static
from facturation.models import Utilisateur

def home_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, "role", "") == "Caissier":
            return redirect("caisse:index")
        return redirect("gestionnaire:dashboard")

    role_counts = {
        "caissiers": Utilisateur.objects.filter(role="Caissier", is_active=True).count(),
        "gestionnaires": Utilisateur.objects.filter(role="Gestionnaire", is_active=True).count(),
    }
    return render(request, "home.html", {"role_counts": role_counts})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    # Tailwind development server
    path("__reload__/", include("django_browser_reload.urls")),
    # apps urls
    path('caisse/', include('apps.caisse.urls')),
    path('dashboard/', include('apps.gestionnaire.urls')),
    path('rapport/', include('apps.report.urls')),
    path('articles/', include('apps.articles.urls')),
    path('clients/', include('apps.clients.urls')),
    path('auth/', include('apps.authentification.urls')),
    path('parametre/', include('apps.parametre.urls')),
    path('utilisateurs/', include('apps.utilisateurs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
