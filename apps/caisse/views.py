from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import models, transaction
from facturation.models import Article, Client, Facture, DetailFacture, Utilisateur
from decimal import Decimal
import json

@login_required
def index(request):
    """Vue principale de la caisse"""
    # Données de démonstration pour le caissier
    context = {
        'caissier_nom': 'Marie Dubois',
        'caissier_role': 'Caissière'
    }
    return render(request, 'caisse/index.html', context)

@require_http_methods(["GET"])
def search_articles(request):
    """Recherche d'articles par nom ou code-barres"""
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'articles': []})
    
    # Recherche dans les articles actifs
    articles = Article.objects.filter(
        actif=True
    ).filter(
        models.Q(nom__icontains=query) | 
        models.Q(code_barres__icontains=query)
    )[:10]
    
    articles_data = [{
        'id': article.id,
        'nom': article.nom,
        'code_barres': article.code_barres,
        'prix_ttc': float(article.prix_TTC),
        'prix_ht': float(article.prix_HT),
        'tva_rate': float(article.taux_TVA) * 100,
        'stock': article.stock_actuel
    } for article in articles]
    
    return JsonResponse({'articles': articles_data})

@login_required
@require_http_methods(["POST"])
def create_facture(request):
    """Créer une nouvelle facture"""
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        
        if not items:
            return JsonResponse({'error': 'Le panier est vide'}, status=400)
        
        # Utiliser l'utilisateur actuellement connecté
        caissier = request.user
        
        # Gérer le client (nom fourni ou anonyme par défaut)
        client_name = data.get('client_name', '').strip()
        if client_name:
            # Créer ou récupérer un client avec le nom fourni
            client, _ = Client.objects.get_or_create(
                nom=client_name,
                defaults={
                    "type": "Occasionnel",
                    "prenom": "",
                },
            )
        else:
            # Client anonyme par défaut
            client, _ = Client.objects.get_or_create(
                nom="Client de passage",
                defaults={"type": "Occasionnel"},
            )

        montant_ht = Decimal("0")
        montant_tva = Decimal("0")
        montant_ttc = Decimal("0")
        detail_rows = []

        with transaction.atomic():
            for item in items:
                article_id = item.get("article_id")
                quantite = int(item.get("quantite", 0))
                if not article_id or quantite <= 0:
                    return JsonResponse({"error": "Ligne article invalide"}, status=400)

                article = Article.objects.select_for_update().get(id=article_id, actif=True)
                if article.stock_actuel < quantite:
                    return JsonResponse(
                        {"error": f"Stock insuffisant pour {article.nom} (disponible: {article.stock_actuel})"},
                        status=400,
                    )

                line_ht = (article.prix_HT * quantite).quantize(Decimal("0.01"))
                line_ttc = (article.prix_TTC * quantite).quantize(Decimal("0.01"))
                line_tva = (line_ttc - line_ht).quantize(Decimal("0.01"))

                montant_ht += line_ht
                montant_tva += line_tva
                montant_ttc += line_ttc

                detail_rows.append(
                    {
                        "article": article,
                        "quantite": quantite,
                        "prix_unitaire": article.prix_TTC,
                        "remise": Decimal("0"),
                        "total_ligne": line_ttc,
                    }
                )

            facture = Facture.objects.create(
                montant_HT=montant_ht,
                montant_TVA=montant_tva,
                montant_TTC=montant_ttc,
                mode_paiement=data.get("mode_paiement", "especes"),
                client=client,
                caissier=caissier,
            )

            for row in detail_rows:
                DetailFacture.objects.create(facture=facture, **row)
                row["article"].stock_actuel -= row["quantite"]
                row["article"].save(update_fields=["stock_actuel"])
        
        return JsonResponse({
            'success': True,
            'facture_id': facture.id,
            'numero_facture': f'FAC-{facture.id:08d}'
        })
    except Article.DoesNotExist:
        return JsonResponse({'error': "Article introuvable ou inactif"}, status=404)
    except ValueError:
        return JsonResponse({'error': "Format de données invalide"}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
