# Module de Gestion des Articles

## 📋 Vue d'ensemble

Module complet de gestion des articles pour une application de facturation en Django.

## ✨ Fonctionnalités

### 1. **Gestion CRUD des articles**
- Créer des articles avec tous les champs requis
- Éditer les articles existants
- Supprimer les articles
- Afficher la liste des articles avec pagination

### 2. **Modèle riche (Article)**
```python
- code_barres (EAN13, unique)
- nom, description
- prix_ht, prix_ttc, taux_tva
- categorie (Boulangerie, Produits laitiers, Fruits & légumes, Viande, Épicerie, Boissons)
- unite_mesure (Unité, Kg, Litre)
- stock_actuel, stock_minimum
- actif (Boolean)
- Métadonnées: created_at, updated_at
```

### 3. **Recherche et Filtrage**
- Recherche par nom ou code-barres
- Filtrage par catégorie
- Filtrage par statut (actif/inactif)
- Recherche avancée via service

### 4. **Import/Export CSV**
- Importer les articles en masse depuis CSV
- Exporter les articles en CSV
- Gestion des erreurs ligne par ligne
- Mise à jour automatique des articles existants

### 5. **Dashboard avec Statistiques**
- Total d'articles
- Stock total (quantité et valeur)
- Articles en rupture
- Prix moyen
- Répartition par catégorie
- Alertes stock faible

### 6. **Validations métier**
- Validation EAN13 (13 chiffres)
- Validation des prix (positifs)
- Cohérence HT/TTC/TVA
- Stock minimum logique

### 7. **Interface Dark Mode**
- Design modern avec Tailwind CSS
- Thème sombre complet (#121212, #1e1e1e)
- Responsive (mobile, tablet, desktop)
- Icônes et badges informatifs

### 8. **Tests complets**
- Tests du modèle
- Tests des validations
- Tests des services
- Tests des vues
- Tests de recherche et filtrage

## 🚀 Routes disponibles

| Route | Méthode | Description |
|-------|---------|-------------|
| `/articles/` | GET | Liste des articles |
| `/articles/dashboard/` | GET | Dashboard avec stats |
| `/articles/creer/` | GET/POST | Créer un article |
| `/articles/editer/<id>/` | GET/POST | Éditer un article |
| `/articles/supprimer/<id>/` | GET/POST | Supprimer un article |
| `/articles/importer/` | GET/POST | Importer CSV |
| `/articles/exporter/` | GET | Exporter CSV |

## 📦 Structure des fichiers

```
articles/
├── models.py              # Modèle Article avec validations
├── forms.py              # Formulaire ArticleForm
├── views.py              # 7 vues + dashboard
├── services.py           # Service métier ArticleService
├── urls.py               # Routes URL
├── admin.py              # Interface admin
├── tests.py              # Tests unitaires
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py   # Migration du modèle
└── templates/articles/
    ├── liste_articles.html
    ├── creer_article.html
    ├── editer_article.html
    ├── importer_articles.html
    ├── confirmer_suppression.html
    └── dashboard.html
```

## 🔧 Installation et Configuration

### 1. Migrations
```bash
python manage.py makemigrations articles
python manage.py migrate articles
```

### 2. Accéder à l'admin Django
```bash
python manage.py createsuperuser
python manage.py runserver
# Aller à http://localhost:8000/admin/
```

### 3. Utiliser le module
- Dashboard: `/articles/dashboard/`
- Gestion: `/articles/`

## 📝 Format d'import CSV

Le fichier CSV doit contenir les colonnes suivantes:

```csv
Code-barres,Nom,Description,Prix HT,Prix TTC,TVA,Catégorie,Unité,Stock actuel,Stock minimum,Actif
1234567890123,Baguette,"Pain blanc",0.80,0.85,5.5,Boulangerie,Unité,50,10,Oui
```

**Colonnes requises:**
- Code-barres
- Nom
- Prix HT
- Prix TTC

**Colonnes optionnelles:**
- Description
- TVA (défaut: 5.5)
- Catégorie (défaut: Épicerie)
- Unité (défaut: Unité)
- Stock actuel (défaut: 0)
- Stock minimum (défaut: 5)
- Actif (défaut: Oui)

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test articles

# Lancer un test spécifique
python manage.py test articles.tests.ArticleModelTests

# Avec coverage
pip install coverage
coverage run --source='articles' manage.py test articles
coverage report
```

## 📊 API Service (ArticleService)

### Méthodes disponibles

```python
from articles.services import ArticleService

# Statistiques
stats = ArticleService.get_statistics()

# Articles en stock faible
low_stock = ArticleService.get_articles_low_stock()

# Recherche
results = ArticleService.search_articles('baguette')

# Par catégorie
articles = ArticleService.get_articles_by_category('boulangerie')

# Calculs
ttc = ArticleService.calculate_ttc(100, 5.5)  # 105.5
is_valid = ArticleService.validate_prix(100, 105.5, 5.5)  # True
```

## 🎨 Personnalisation

### Ajouter une catégorie
Modifiez `Article.CATEGORIE_CHOICES` dans `models.py`

### Ajouter un champ
```python
# Dans models.py
class Article(models.Model):
    # ... champs existants ...
    nouveau_champ = models.CharField(max_length=100)

# Puis:
python manage.py makemigrations articles
python manage.py migrate articles
```

## 🔐 Sécurité

- ✓ CSRF protection sur tous les formulaires
- ✓ Validations côté serveur complètes
- ✓ Sanitization des données CSV
- ✓ Validation EAN13 stricte
- ✓ Gestion des erreurs robuste

## 📈 Performance

- Index sur: code_barres, categorie, actif
- Pagination disponible pour les grandes listes
- ORM optimisé (select_related, prefetch_related)
- Export CSV efficace

## 🐛 Dépannage

### Erreur: "Code-barres doit être EAN13"
- Vérifiez que le code contient exactement 13 chiffres

### Erreur: "Code-barres dupliqué"
- Le code-barres doit être unique
- Vérifiez dans la base de données

### Erreur: "Prix TTC incohérent"
- Vérifiez la formule: Prix TTC = Prix HT × (1 + TVA%)
- Exemple: 100 × 1.055 = 105.5

## 📞 Support

Pour plus d'informations ou des problèmes, vérifiez:
1. Les logs Django
2. Les tests unitaires
3. La documentation de Django
