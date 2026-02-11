from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.db import models
from django.http import JsonResponse
from facturation.models import Article, Client, Facture, DetailFacture, Utilisateur
from decimal import Decimal
from django.contrib.postgres.search import SearchVector
import json
from django.http import JsonResponse

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



def create_facture(request):
    if request.method == 'POST':
        articles = json.loads(request.body)
        montant= 0

        for article in articles:
            produit= Article.objects.get(id=article['id'])
            produit.stock_actuel-=article['quantite']
            produit.save()
            montant+= (article['prix_TTC']*article['quantite'])

        facture= Facture.objects.create(
            montant=Decimal(montant), 
            client=Client.objects.first(), 
            caissier=Utilisateur.objects.first()
        )
        for article in articles:
            DetailFacture.objects.create(
                facture=facture,
                article=Article.objects.get(id=article['id']),
                quantite=article['quantite'],
                prix_unitaire=Decimal(article['prix_TTC']),
                total_ligne=Decimal(article['prix_TTC']*article['quantite'])
            )

        return JsonResponse({
            'success': True,
            'facture_id': facture.id,
            'numero_facture': f'FAC-{facture.id}',
            'montant': float(facture.montant)
        })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    

