from django.core.management.base import BaseCommand
from facturation.models import Article


class Command(BaseCommand):
    help = 'Crée des articles de démonstration pour tester le module'

    def handle(self, *args, **options):
        articles_data = [
            {
                'code_barres': '3017620425035',
                'nom': 'Baguette Tradition',
                'description': 'Pain blanc traditionnel français',
                'prix_HT': 0.75,
                'prix_TTC': 0.79,
                'taux_TVA': 0.055,
                'categorie': 'boulangerie',
                'unite_mesure': 'unite',
                'stock_actuel': 50,
                'stock_minimum': 10,
            },
            {
                'code_barres': '3330461112330',
                'nom': 'Yaourt Nature',
                'description': 'Yaourt nature 125g',
                'prix_HT': 0.60,
                'prix_TTC': 0.63,
                'taux_TVA': 0.055,
                'categorie': 'produits_laitiers',
                'unite_mesure': 'unite',
                'stock_actuel': 120,
                'stock_minimum': 20,
            },
            {
                'code_barres': '3596710119856',
                'nom': 'Pommes Gala',
                'description': 'Pommes fraîches de saison',
                'prix_HT': 1.50,
                'prix_TTC': 1.58,
                'taux_TVA': 0.055,
                'categorie': 'fruits_legumes',
                'unite_mesure': 'kg',
                'stock_actuel': 80,
                'stock_minimum': 15,
            },
            {
                'code_barres': '3760118647126',
                'nom': 'Steak Haché',
                'description': 'Steak haché 5% MG 200g',
                'prix_HT': 2.99,
                'prix_TTC': 3.15,
                'taux_TVA': 0.055,
                'categorie': 'viande',
                'unite_mesure': 'unite',
                'stock_actuel': 45,
                'stock_minimum': 10,
            },
            {
                'code_barres': '3228857001201',
                'nom': 'Riz Complet',
                'description': 'Riz complet biologique 500g',
                'prix_HT': 1.20,
                'prix_TTC': 1.27,
                'taux_TVA': 0.055,
                'categorie': 'epicerie',
                'unite_mesure': 'unite',
                'stock_actuel': 200,
                'stock_minimum': 30,
            },
            {
                'code_barres': '3421063100142',
                'nom': 'Eau Minérale',
                'description': 'Eau minérale naturelle 1,5L',
                'prix_HT': 0.50,
                'prix_TTC': 0.53,
                'taux_TVA': 0.055,
                'categorie': 'boissons',
                'unite_mesure': 'litre',
                'stock_actuel': 150,
                'stock_minimum': 50,
            },
            {
                'code_barres': '3012345678901',
                'nom': 'Lait Entier',
                'description': 'Lait frais entier 1L',
                'prix_HT': 0.85,
                'prix_TTC': 0.90,
                'taux_TVA': 0.055,
                'categorie': 'produits_laitiers',
                'unite_mesure': 'litre',
                'stock_actuel': 2,
                'stock_minimum': 10,
            },
            {
                'code_barres': '3012345678902',
                'nom': 'Fromage Emmental',
                'description': 'Emmental français 200g',
                'prix_HT': 2.50,
                'prix_TTC': 2.64,
                'taux_TVA': 0.055,
                'categorie': 'produits_laitiers',
                'unite_mesure': 'unite',
                'stock_actuel': 0,
                'stock_minimum': 5,
            },
        ]

        created = 0
        for data in articles_data:
            article, is_created = Article.objects.get_or_create(
                code_barres=data['code_barres'],
                defaults=data
            )
            if is_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f'✓ {created} articles créés avec succès')
        )
