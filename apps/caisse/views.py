from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.db import models
from facturation.models import Article, Client, Facture, DetailFacture, Utilisateur
from decimal import Decimal
from django.contrib.postgres.search import SearchVector

def index(request):
    """Vue principale de la caisse"""
    # Données de démonstration pour le caissier
    context = {
        'caissier_nom': 'Marie Dubois',
        'caissier_role': 'Caissière'
    }
    return render(request, 'caisse/index.html', context)


def search_articles(request):
    if request.method == 'GET':
        query= request.GET.get('q', '')
        if query:
            article= Article.objects.annotate(
                search=SearchVector('code_barres', 'nom')
            ).filter(search=query)
            return render(request, 'caisse/search_results.html', {'articles': article})
    return render(request, 'caisse/search_results.html', {'articles': []})


@require_http_methods(["POST"])
def create_facture(request)
