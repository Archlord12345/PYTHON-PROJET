# Guide d'Installation - Module Articles

## 📋 Pré-requis

- Python 3.8+
- Django 6.0+
- PostgreSQL 12+ (ou SQLite pour développement)

## 🔧 Installation Rapide

### 1. **Appliquer les migrations**

```bash
cd /home/hp/Images/Archive
python manage.py migrate articles
```

### 2. **Créer un superutilisateur** (si nécessaire)

```bash
python manage.py createsuperuser
```

### 3. **Charger les données de démonstration** (optionnel)

```bash
python manage.py create_sample_articles
```

### 4. **Démarrer le serveur**

```bash
python manage.py runserver
```

### 5. **Accéder au module**

- **Dashboard:** http://localhost:8000/articles/dashboard/
- **Gestion:** http://localhost:8000/articles/
- **Admin Django:** http://localhost:8000/admin/

## 📝 Configuration PostgreSQL

Si vous utilisez PostgreSQL, assurez-vous que vos identifiants sont corrects dans `.env`:

```env
DB_NAME=facturation
DB_USER=ravel
DB_PASSWORD=ravel
DB_HOST=localhost
PORT=5432
```

**Créer la base de données (si nécessaire):**

```bash
sudo -u postgres createdb -O ravel facturation
```

**Créer l'utilisateur PostgreSQL:**

```bash
sudo -u postgres createuser ravel -P
# Entrez le mot de passe: ravel
```

## 🧪 Lancer les tests

```bash
# Tous les tests
python manage.py test articles

# Avec rapport de couverture
pip install coverage
coverage run --source='articles' manage.py test articles
coverage report
coverage html  # Génère un rapport HTML
```

## 📊 Vérification

Après installation, vérifiez que tout fonctionne:

```bash
# Vérifier la configuration
python manage.py check

# Lister les migrations
python manage.py showmigrations articles

# Vérifier que le module est bien enregistré
python manage.py shell
>>> from articles.models import Article
>>> Article.objects.count()
```

## 🎯 Utilisation de base

### Via l'interface web

1. **Dashboard** (`/articles/dashboard/`)
   - Vue d'ensemble des statistiques
   - Alertes sur le stock faible
   - Actions rapides

2. **Liste des articles** (`/articles/`)
   - Tableau avec tous les articles
   - Recherche par nom/code-barres
   - Filtrage par catégorie
   - Édition rapide
   - Suppression

3. **Créer un article** (`/articles/creer/`)
   - Formulaire complet
   - Validation des données
   - Calcul automatique du TTC

4. **Importer des articles** (`/articles/importer/`)
   - Upload de fichier CSV
   - Gestion des erreurs
   - Mise à jour en masse

5. **Exporter les articles** (`/articles/exporter/`)
   - Télécharge tous les articles
   - Format CSV compatible Excel

### Via Django Admin (`/admin/`)

- Accès complet aux articles
- Filtres avancés
- Recherche
- Actions personnalisées

### Via le code Python

```python
from articles.models import Article
from articles.services import ArticleService

# Créer un article
article = Article.objects.create(
    code_barres='1234567890123',
    nom='Mon Article',
    prix_ht=10.0,
    prix_ttc=10.55,
    taux_tva=5.5,
    categorie='epicerie',
    stock_actuel=50,
    stock_minimum=10,
)

# Récupérer les statistiques
stats = ArticleService.get_statistics()
print(f"Total d'articles: {stats['total_articles']}")

# Récupérer les articles en stock faible
low_stock = ArticleService.get_articles_low_stock()

# Chercher des articles
results = ArticleService.search_articles('baguette')
```

## 🚨 Dépannage

### Erreur: "Aucune table 'articles_article'"

**Solution:** Appliquer les migrations

```bash
python manage.py migrate articles
```

### Erreur: "Code-barres doit être EAN13 (13 chiffres)"

**Solution:** Vérifiez que votre code contient exactement 13 chiffres numériques

```python
# ✓ Correct
code_barres = '1234567890123'

# ✗ Incorrect
code_barres = '123456789012'    # 12 chiffres
code_barres = 'ABC1234567890'   # Contient des lettres
```

### Erreur: "Prix TTC incohérent"

**Solution:** Vérifiez la formule: TTC = HT × (1 + TVA%)

```python
# ✓ Correct
prix_ht = 100
taux_tva = 5.5
prix_ttc = 100 * 1.055  # 105.5

# ✗ Incorrect
prix_ttc = 110  # Incohérent avec HT et TVA
```

### Erreur de connexion PostgreSQL

**Solutions:**
1. Vérifiez que PostgreSQL est en cours d'exécution
2. Vérifiez vos identifiants dans `.env`
3. Vérifiez que la base de données existe
4. Vérifiez que l'utilisateur a les permissions

```bash
# Tester la connexion
psql -U ravel -d facturation -h localhost
```

### Page blanche ou erreur 500

**Solutions:**
1. Vérifiez les logs Django:
   ```bash
   tail -f logs/django.log
   ```
2. Activez DEBUG dans settings:
   ```python
   DEBUG = True
   ```
3. Vérifiez que les migrations sont appliquées:
   ```bash
   python manage.py migrate
   ```

## 📦 Fichiers générés

Après installation, vérifiez la présence de:

```
articles/
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py         ✓
├── management/commands/
│   ├── __init__.py
│   └── create_sample_articles.py ✓
├── templates/articles/
│   ├── dashboard.html          ✓
│   ├── liste_articles.html     ✓
│   ├── creer_article.html      ✓
│   ├── editer_article.html     ✓
│   ├── importer_articles.html  ✓
│   └── confirmer_suppression.html ✓
├── __init__.py
├── admin.py                     ✓
├── apps.py
├── config.py                    ✓
├── forms.py                     ✓
├── models.py                    ✓
├── services.py                  ✓
├── tests.py                     ✓
├── urls.py                      ✓
├── views.py                     ✓
└── README.md                    ✓
```

## 🎓 Prochaines étapes

1. **Personnaliser les catégories** (`config.py`)
2. **Ajouter des images aux articles** (nouveau champ)
3. **Intégrer avec la facturation** (FK vers Facture)
4. **Ajouter des codes de remise** (nouveau modèle)
5. **Historique de prix** (tracking des changements)
6. **Notifications de stock** (emails/SMS)

## 📞 Besoin d'aide?

Consultez:
- [README.md](README.md) - Documentation détaillée
- [models.py](models.py) - Structure du modèle
- [services.py](services.py) - Fonctions métier
- [tests.py](tests.py) - Exemples d'utilisation
