from django.db.models import Q, Sum, Count, Avg, F
from django.db.models.functions import Coalesce
from facturation.models import Article


class ArticleService:
    """Service métier pour les articles"""

    @staticmethod
    def get_articles_low_stock():
        """Récupère les articles en rupture ou stock faible"""
        return Article.objects.filter(
            Q(stock_actuel__lte=F('stock_minimum')) | 
            Q(stock_actuel=0),
            actif=True
        ).values('id', 'code_barres', 'nom', 'stock_actuel', 'stock_minimum')

    @staticmethod
    def get_statistics():
        """Retourne les statistiques du catalogue"""
        from decimal import Decimal
        
        articles = Article.objects.filter(actif=True)
        all_articles = Article.objects.all()
        
        # Calculer la valeur du stock et prix moyen manuellement
        valeur_stock = Decimal('0')
        total_prix = Decimal('0')
        
        for article in articles:
            valeur_stock += article.stock_actuel * article.prix_HT
            total_prix += article.prix_HT
        
        prix_moyen = (total_prix / articles.count()) if articles.count() > 0 else Decimal('0')
        
        category_labels = dict(Article.CATEGORIE_CHOICES)
        category_rows = list(
            articles.values('categorie')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        for row in category_rows:
            row['label'] = category_labels.get(row['categorie'], row['categorie'])

        return {
            'total_articles': all_articles.count(),
            'articles_actifs': articles.count(),
            'articles_inactifs': all_articles.filter(actif=False).count(),
            'stock_total': articles.aggregate(
                total=Coalesce(Sum('stock_actuel'), 0)
            )['total'],
            'valeur_stock': valeur_stock,
            'prix_moyen': prix_moyen,
            'articles_rupture': articles.filter(stock_actuel=0).count(),
            'articles_stock_faible': articles.filter(
                stock_actuel__gt=0,
                stock_actuel__lte=F('stock_minimum')
            ).count(),
            'par_categorie': category_rows,
        }

    @staticmethod
    def validate_prix(prix_ht, prix_ttc, taux_tva):
        """Valide la cohérence entre prix HT, TTC et TVA"""
        expected_ttc = float(prix_ht) * (1 + float(taux_tva) / 100)
        return abs(float(prix_ttc) - expected_ttc) < 0.01

    @staticmethod
    def calculate_ttc(prix_ht, taux_tva):
        """Calcule le prix TTC à partir du HT et TVA"""
        return float(prix_ht) * (1 + float(taux_tva) / 100)

    @staticmethod
    def search_articles(query):
        """Recherche avancée sur les articles"""
        return Article.objects.filter(
            Q(code_barres__icontains=query) |
            Q(nom__icontains=query) |
            Q(description__icontains=query)
        ).values('id', 'code_barres', 'nom', 'categorie', 'prix_HT', 'stock_actuel')

    @staticmethod
    def get_articles_by_category(categorie):
        """Récupère les articles par catégorie"""
        return Article.objects.filter(
            categorie=categorie,
            actif=True
        ).values('id', 'nom', 'prix_HT', 'prix_TTC', 'stock_actuel')
