from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from facturation.models import Article, Client, Facture, DetailFacture
from decimal import Decimal


@login_required
def dashboard_view(request):
    """Vue du tableau de bord avec statistiques clés"""
    
    # Période par défaut : 30 derniers jours
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # --- STATISTIQUES VENTES ---
    # Total des ventes
    total_sales = Facture.objects.aggregate(
        total=Sum('montant_TTC')
    )['total'] or Decimal('0')
    
    # Ventes des 30 derniers jours
    recent_sales = Facture.objects.filter(
        date_facture__date__gte=thirty_days_ago
    ).aggregate(total=Sum('montant_TTC'))['total'] or Decimal('0')
    
    # Nombre de factures
    total_invoices = Facture.objects.count()
    recent_invoices = Facture.objects.filter(
        date_facture__date__gte=thirty_days_ago
    ).count()
    
    # Panier moyen
    avg_cart = Facture.objects.aggregate(
        avg=Avg('montant_TTC')
    )['avg'] or Decimal('0')
    
    # --- STATISTIQUES ARTICLES ---
    total_articles = Article.objects.count()
    active_articles = Article.objects.filter(actif=True).count()
    low_stock_articles = Article.objects.filter(
        actif=True,
        stock_actuel__lte=F('stock_minimum')
    ).count()
    out_of_stock_articles = Article.objects.filter(
        actif=True,
        stock_actuel=0
    ).count()
    
    # Top 5 des articles les plus vendus
    top_articles = DetailFacture.objects.values(
        'article__nom', 'article__code_barres'
    ).annotate(
        total_qty=Sum('quantite'),
        total_revenue=Sum('total_ligne')
    ).order_by('-total_qty')[:5]
    
    # --- STATISTIQUES CLIENTS ---
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(
        facture__isnull=False
    ).distinct().count()
    new_clients_30d = Client.objects.filter(
        facture__date_facture__date__gte=thirty_days_ago
    ).distinct().count()
    
    # Top 5 clients par montant dépensé
    top_clients = Facture.objects.values(
        'client__nom', 'client__prenom'
    ).annotate(
        total_spent=Sum('montant_TTC'),
        invoice_count=Count('id')
    ).order_by('-total_spent')[:5]
    
    # --- VENTES PAR JOUR (30 derniers jours) ---
    sales_by_day = []
    for i in range(30, -1, -1):
        date = today - timedelta(days=i)
        day_sales = Facture.objects.filter(
            date_facture__date=date
        ).aggregate(total=Sum('montant_TTC'))['total'] or Decimal('0')
        sales_by_day.append({
            'date': date.strftime('%d/%m'),
            'amount': float(day_sales)
        })
    
    # --- VENTES PAR MODE DE PAIEMENT ---
    payment_methods = Facture.objects.values('mode_paiement').annotate(
        count=Count('id'),
        total=Sum('montant_TTC')
    ).order_by('-total')
    
    context = {
        # KPI Cards
        'total_sales': total_sales,
        'recent_sales': recent_sales,
        'total_invoices': total_invoices,
        'recent_invoices': recent_invoices,
        'avg_cart': avg_cart,
        'total_articles': total_articles,
        'active_articles': active_articles,
        'low_stock_articles': low_stock_articles,
        'out_of_stock_articles': out_of_stock_articles,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'new_clients_30d': new_clients_30d,
        
        # Tables
        'top_articles': top_articles,
        'top_clients': top_clients,
        
        # Charts data
        'sales_by_day': sales_by_day,
        'payment_methods': payment_methods,
        
        # Période
        'period_start': thirty_days_ago.strftime('%d/%m/%Y'),
        'period_end': today.strftime('%d/%m/%Y'),
    }
    
    return render(request, 'gestionnaire/dashboard.html', context)