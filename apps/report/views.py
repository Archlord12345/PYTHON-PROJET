from django.shortcuts import render


def report_view(request):
    context = {
        'stats_ventes': [
            {'label': 'CA Total', 'value': '34 700 FCFA', 'trend': '+18% vs période précédente', 'trend_up': True},
            {'label': 'Transactions', 'value': '432', 'trend': 'Sur la période', 'trend_up': False},
            {'label': 'Panier moyen', 'value': '80 FCFA', 'trend': '+5% vs période précédente', 'trend_up': True},
            {'label': 'Produits vendus', 'value': '5,234', 'trend': 'Articles au total', 'trend_up': False},
        ],
        'paiements': [
            {'label': 'Carte bancaire', 'amount': '12 500 FCFA', 'color': 'bg-blue-500'},
            {'label': 'Espèces', 'amount': '8 300 FCFA', 'color': 'bg-emerald-500'},
            {'label': 'Chèque', 'amount': '2 100 FCFA', 'color': 'bg-amber-500'},
            {'label': 'Ticket restaurant', 'amount': '1 800 FCFA', 'color': 'bg-purple-500'},
        ],
        'mouvements': [
            {'name': 'Lait Entier 1L', 'desc': '+48 unités • Réception', 'time': 'Il y a 2h'},
            {'name': 'Pâtes Penne 500g', 'desc': '-12 unités • Vente', 'time': 'Il y a 3h'},
        ],
        'cartes_finances': [
            {'label': 'CA HT', 'value': '29 145 FCFA', 'sub': 'Hors taxes'},
            {'label': 'TVA Collectée', 'value': '5 555 FCFA', 'sub': 'À reverser'},
            {'label': 'CA TTC', 'value': '34 700 FCFA', 'sub': 'Toutes taxes comprises'},
        ],
        'tva': [
            {'rate': 'TVA 5,5%', 'base': '18 230 FCFA', 'amount': '1 003 FCFA'},
            {'rate': 'TVA 10%', 'base': '5 420 FCFA', 'amount': '542 FCFA'},
            {'rate': 'TVA 20%', 'base': '5 495 FCFA', 'amount': '1 099 FCFA'},
        ],
        'stock_total': '125 430 FCFA',
    }
    return render(request, 'report/report.html', context)
