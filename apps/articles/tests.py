from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from facturation.models import Article
from .services import ArticleService


class ArticleModelTests(TestCase):
    """Tests du modèle Article"""

    def setUp(self):
        self.article = Article.objects.create(
            code_barres='1234567890123',
            nom='Baguette',
            prix_HT=0.80,
            prix_TTC=0.85,
            taux_TVA=0.055,
            categorie='boulangerie',
            stock_actuel=50,
            stock_minimum=10,
        )

    def test_article_creation(self):
        """Test la création d'un article"""
        self.assertEqual(self.article.code_barres, '1234567890123')
        self.assertEqual(self.article.nom, 'Baguette')
        self.assertTrue(self.article.actif)

    def test_article_string_representation(self):
        """Test la représentation en string"""
        self.assertEqual(str(self.article), '1234567890123 - Baguette')

    def test_low_stock_detection(self):
        """Test la détection de stock faible"""
        self.assertFalse(self.article.is_low_stock())
        
        self.article.stock_actuel = 5
        self.assertTrue(self.article.is_low_stock())

    def test_out_of_stock_detection(self):
        """Test la détection de rupture"""
        self.assertFalse(self.article.is_out_of_stock())
        
        self.article.stock_actuel = 0
        self.assertTrue(self.article.is_out_of_stock())

    def test_stock_status(self):
        """Test le statut du stock"""
        self.assertEqual(self.article.get_stock_status(), 'ok')
        
        self.article.stock_actuel = 5
        self.assertEqual(self.article.get_stock_status(), 'faible')
        
        self.article.stock_actuel = 0
        self.assertEqual(self.article.get_stock_status(), 'rupture')

    def test_invalid_ean13(self):
        """Test la validation du code-barres"""
        article = Article(
            code_barres='123',  # EAN13 invalide
            nom='Test',
            prix_HT=1.0,
            prix_TTC=1.06,
            taux_TVA=0.055,
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_negative_price_validation(self):
        """Test la validation des prix négatifs"""
        article = Article(
            code_barres='1234567890123',
            nom='Test',
            prix_HT=-1.0,
            prix_TTC=1.06,
            taux_TVA=0.055,
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_price_coherence_validation(self):
        """Test la validation de cohérence HT/TTC"""
        article = Article(
            code_barres='1234567890123',
            nom='Test',
            prix_HT=100.0,
            prix_TTC=50.0,  # Incohérent
            taux_TVA=0.055,
        )
        with self.assertRaises(ValidationError):
            article.full_clean()

    def test_unique_code_barres(self):
        """Test l'unicité du code-barres"""
        with self.assertRaises(Exception):
            Article.objects.create(
                code_barres='1234567890123',  # Même que self.article
                nom='Autre article',
                prix_HT=1.0,
                prix_TTC=1.06,
                taux_TVA=0.055,
            )


class ArticleServiceTests(TestCase):
    """Tests du service métier"""

    def setUp(self):
        for i in range(5):
            Article.objects.create(
                code_barres=f'123456789012{i}',
                nom=f'Article {i}',
                prix_HT=float(i + 1),
                prix_TTC=float((i + 1) * 1.055),
                taux_TVA=0.055,
                categorie='epicerie',
                stock_actuel=i * 10,
                stock_minimum=5,
                actif=i % 2 == 0,
            )

    def test_get_low_stock_articles(self):
        """Test la récupération des articles en stock faible"""
        low_stock = ArticleService.get_articles_low_stock()
        self.assertTrue(len(low_stock) > 0)

    def test_get_statistics(self):
        """Test le calcul des statistiques"""
        stats = ArticleService.get_statistics()
        
        self.assertIn('total_articles', stats)
        self.assertIn('articles_actifs', stats)
        self.assertIn('stock_total', stats)
        self.assertEqual(stats['total_articles'], 5)

    def test_calculate_ttc(self):
        """Test le calcul du prix TTC"""
        ttc = ArticleService.calculate_ttc(100, 5.5)
        self.assertAlmostEqual(ttc, 105.5, places=2)

    def test_validate_prix(self):
        """Test la validation des prix"""
        self.assertTrue(ArticleService.validate_prix(100, 105.5, 5.5))
        self.assertFalse(ArticleService.validate_prix(100, 200, 5.5))


class ArticleViewsTests(TestCase):
    """Tests des vues"""

    def setUp(self):
        self.client = Client()
        self.article = Article.objects.create(
            code_barres='1234567890123',
            nom='Test Article',
            prix_HT=10.0,
            prix_TTC=10.55,
            taux_TVA=0.055,
            categorie='epicerie',
            stock_actuel=50,
            stock_minimum=10,
        )

    def test_liste_articles_view(self):
        """Test la vue de liste"""
        response = self.client.get(reverse('articles:liste_articles'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')

    def test_dashboard_view(self):
        """Test la vue du dashboard"""
        response = self.client.get(reverse('articles:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('stats', response.context)

    def test_creer_article_view_get(self):
        """Test la vue de création (GET)"""
        response = self.client.get(reverse('articles:creer_article'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_editer_article_view_get(self):
        """Test la vue d'édition (GET)"""
        response = self.client.get(
            reverse('articles:editer_article', args=[self.article.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_search_articles(self):
        """Test la recherche"""
        response = self.client.get(
            reverse('articles:liste_articles') + '?search=Test'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Article')

    def test_filter_by_category(self):
        """Test le filtrage par catégorie"""
        response = self.client.get(
            reverse('articles:liste_articles') + '?categorie=epicerie'
        )
        self.assertEqual(response.status_code, 200)

