<p align="center">
  <img src="static/images/logo.png" alt="Logo Facturation" width="200"/>
</p>

<h1 align="center">Application de Facturation</h1>

<p align="center">
  Application web de gestion de facturation développée avec Django.
</p>

## 🎯 Nouvelles Fonctionnalités (2024)

### � Dashboard Fonctionnel
- Vue d'ensemble avec statistiques clés (ventes, articles, clients, factures)
- Graphiques des ventes par jour/semaine/mois/année
- Top 5 des articles les plus vendus
- Top 5 des meilleurs clients
- Répartition des modes de paiement
- Alertes de stock bas

### �👥 Système de Rôles Avancé
Trois types de comptes avec accès différenciés :

| Rôle | Dashboard | Caisse | Articles | Clients | Rapports | Paramètres | Utilisateurs |
|------|-----------|--------|----------|---------|----------|------------|--------------|
| **Caissier** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Gestionnaire** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Administrateur** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 🔐 Comptes par défaut

| Login | Mot de passe | Rôle |
|-------|--------------|------|
| `admin` | `admin` | Administrateur |
| `gestionnaire` | `gestionnaire` | Gestionnaire |
| `caissiere` | `caissiere` | Caissier |

### 👤 Module Utilisateurs (Admin uniquement)
- Créer des comptes (Caissier, Gestionnaire, Administrateur)
- Modifier les utilisateurs existants
- Activer/Désactiver des comptes
- Supprimer des utilisateurs
- Statistiques par rôle

### 💰 Caisse Améliorée
- **Client nommé ou anonyme** : Possibilité d'entrer un nom de client ou laisser anonyme
- **Effet de flou** : Arrière-plan flouté quand le champ code-barres est actif
- **Liste d'articles** : Affichage de tous les articles dans le modal de recherche
- **Placeholder visible** : Texte d'aide plus visible dans le champ de recherche

### 📦 Gestion des Articles
- **Prix TTC automatique** : Calcul automatique du prix TTC à partir du prix HT et du taux de TVA
- **TVA personnalisable** : Saisie libre du taux de TVA (pas seulement les valeurs prédéfinies)
- Affichage en temps réel du prix TTC calculé

### 📁 Transfert de Données
Système de fixtures pour faciliter le transfert entre machines :
```bash
# Sauvegarder les données
./backup_data.sh

# Restaurer sur une nouvelle machine
python manage.py loaddata apps/utilisateurs/fixtures/users.json
python manage.py loaddata apps/utilisateurs/fixtures/articles.json
```

## 👥 Chefs d'équipe

- `authentification` + `gestionnaire` : Tchinda (chef), Miguel (sous-chef)
- `caisse` : Charles
- `phone` : Nghomsi

## 🗃️ Modèle de données

### 🔑 Entités principales

#### 1. Client
- **📝 Description** : Représente un client de l'entreprise
- **📋 Champs** :
  - `nom` : Nom du client
  - `prenom` : Prénom du client
  - `type` : Type de client (enregistre/anonyme/occasionnel)
  - `email` : Adresse email (unique, optionnel)
  - `telephone` : Numéro de téléphone (optionnel)
  - `adresse` : Adresse postale (optionnel)

#### 2. Utilisateur
- **📝 Description** : Compte utilisateur pour l'accès au système
- **📋 Champs** :
  - `login` : Identifiant de connexion (unique)
  - `password` : Mot de passe (hashé)
  - `role` : Rôle de l'utilisateur (Administrateur/Gestionnaire/Caissier)
  - `is_active` : Statut du compte
  - `date_joined` : Date de création

#### 3. Article
- **📝 Description** : Produit en vente
- **📋 Champs** :
  - `code_barres` : Code-barres unique
  - `nom` : Désignation de l'article
  - `description` : Description détaillée
  - `prix_HT` : Prix hors taxes
  - `prix_TTC` : Prix TTC (calculé automatiquement)
  - `taux_TVA` : Taux de TVA
  - `categorie` : Catégorie de l'article
  - `stock_actuel` : Quantité en stock
  - `stock_minimum` : Seuil d'alerte de stock
  - `actif` : Article actif ou non

### 💰 Transactions

#### 4. Facture
- **📝 Description** : Document de vente
- **🔗 Relations** :
  - `client` : Référence au client
  - `caissier` : Utilisateur ayant créé la facture
- **📋 Champs** :
  - `date_facture` : Date de création (auto)
  - `montant_HT` : Montant hors taxes
  - `montant_TVA` : Montant de la TVA
  - `montant_TTC` : Montant TTC
  - `mode_paiement` : Mode de paiement (espèces, carte, etc.)

#### 5. DetailFacture
- **📝 Description** : Ligne de détail d'une facture
- **🔗 Relations** :
  - `facture` : Facture parente
  - `article` : Article concerné
- **📋 Champs** :
  - `quantite` : Quantité vendue
  - `prix_unitaire` : Prix à l'unité
  - `remise` : Remise appliquée
  - `total_ligne` : Total de la ligne

## 📋 Prérequis

- Python 3.8+
- PostgreSQL 12+

### 🔧 Configuration de PostgreSQL

1. **📦 Installation**
   - Sous Ubuntu/Debian :
     ```bash
     sudo apt update
     sudo apt install postgresql postgresql-contrib
     ```
   - Sous macOS (avec Homebrew) :
     ```bash
     brew install postgresql
     ```

2. **💾 Création de la base de données**
   ```bash
   # Se connecter à PostgreSQL
   sudo -u postgres psql
   
   # Créer un utilisateur (si nécessaire)
   CREATE USER mon_utilisateur WITH PASSWORD 'mon_mot_de_passe' CREATEDB;
   
   # Créer la base de données
   CREATE DATABASE facturation OWNER mon_utilisateur;
   
   # Accorder les privilèges
   GRANT ALL PRIVILEGES ON DATABASE facturation TO mon_utilisateur;
   
   # Quitter psql
   \q
   ```

3. **🐍 Installation du connecteur Python**
Le package `psycopg2-binary` est déjà inclus dans `requirements.txt`

## 🚀 Installation

1. Cloner le dépôt :
   ```bash
   git clone [URL_DU_REPO]
   cd facturation
   ```

2. Créer un environnement virtuel et l'activer :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Linux/Mac
   # ou
   .\venv\Scripts\activate  # Sur Windows
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement :
   Créer un fichier `.env` à la racine du projet avec les variables nécessaires (voir la section Configuration).

5. Appliquer les migrations :
   ```bash
   python manage.py migrate
   ```

6. **Charger les données de démonstration (optionnel)** :
   ```bash
   python manage.py loaddata apps/utilisateurs/fixtures/users.json
   python manage.py loaddata apps/utilisateurs/fixtures/articles.json
   ```

7. Démarrer le serveur de développement :
   
   Utilisez le script `run.sh` pour démarrer à la fois le serveur Django et le watcher Tailwind dans un seul terminal :
   ```bash
   # Rendre le script exécutable (une seule fois)
   chmod +x run.sh
   
   # Démarrer le serveur
   ./run.sh
   ```
   
   Ce script démarre automatiquement :
   - Le serveur de développement Django
   - Le watcher Tailwind pour la compilation des fichiers CSS
   
   Appuyez sur `Ctrl+C` pour arrêter proprement les deux processus.

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
SECRET_KEY=votre_secret_key
DEBUG=True

# Paramètres de la BD
DB_NAME=facturation
DB_USER=user_name
DB_PASSWORD=password
DB_HOST=localhost
PORT=5432
```

## 📁 Structure du projet

```text
facturation/
├── apps/
│   ├── authentification/    # Gestion de l'authentification
│   ├── caisse/              # Gestion des ventes et caisse
│   ├── clients/             # Gestion des clients
│   ├── articles/            # Gestion du catalogue
│   ├── report/              # Rapports et statistiques
│   ├── parametre/           # Paramètres système (Admin uniquement)
│   ├── utilisateurs/        # Gestion des utilisateurs (Admin uniquement)
│   └── gestionnaire/        # Dashboard et navigation
├── facturation/             # Configuration du projet
├── media/                   # Fichiers téléchargés
├── static/                  # Fichiers statiques
├── templates/               # Templates HTML
└── theme/                   # Thème et assets
```

## 🧩 Modules

- `authentification` : Connexion et déconnexion
- `caisse` : Encaissements, ventes, gestion du panier
- `clients` : Gestion des clients et historique d'achats
- `articles` : Catalogue produits, gestion des stocks
- `report` : Rapports de ventes, statistiques
- `parametre` : Configuration système (Admin uniquement)
- `utilisateurs` : Création et gestion des comptes (Admin uniquement)
- `gestionnaire` : Dashboard, sidebar, navigation

## 🌐 Routes principales

| URL | Description | Accès |
|-----|-------------|-------|
| `/auth/login/` | Page de connexion | Public |
| `/gestionnaire/` | Dashboard | Tous |
| `/caisse/` | Caisse | Tous |
| `/articles/` | Gestion des articles | Gestionnaire, Admin |
| `/clients/` | Gestion des clients | Gestionnaire, Admin |
| `/report/` | Rapports | Gestionnaire, Admin |
| `/parametre/` | Paramètres | Admin uniquement |
| `/utilisateurs/` | Gestion des utilisateurs | Admin uniquement |

## 💻 Développement

### 🎨 Configuration de Tailwind CSS

Ce projet utilise `django-tailwind`, une intégration de Tailwind CSS pour Django.

#### ⚙️ Installation et configuration

1. Installation du package :
   ```bash
   pip install django-tailwind
   ```

2. Initialisation de Tailwind :
   ```bash
   python manage.py tailwind init
   ```

3. Installation des dépendances :
   ```bash
   python manage.py tailwind install
   ```

#### 🛠️ Développement

- Utilisez le script `run.sh` pour démarrer le serveur de développement et le watcher Tailwind en une seule commande.
- Les fichiers de configuration se trouvent dans le dossier `theme/`
- Les fichiers CSS générés sont disponibles dans `static_src/` et copiés automatiquement vers `static/`

## 📦 Transfert de données entre machines

### Sauvegarde
```bash
./backup_data.sh
```

### Restauration
```bash
python manage.py loaddata apps/utilisateurs/fixtures/users.json
python manage.py loaddata apps/utilisateurs/fixtures/articles.json
python manage.py loaddata apps/utilisateurs/fixtures/clients.json
python manage.py loaddata apps/utilisateurs/fixtures/factures.json
python manage.py loaddata apps/utilisateurs/fixtures/details.json
```

## 👥 Travail d'équipe et bonnes pratiques

### 🏗️ Architecture modulaire

Ce projet suit une architecture modulaire où chaque équipe peut travailler sur un module spécifique.

#### 📂 Structure des modules

Chaque module se trouve dans le dossier `apps/` et contient :
```text
mon_module/
├── migrations/     # Migrations spécifiques au module
├── static/         # Fichiers statiques du module
├── templates/      # Templates spécifiques au module
├── fixtures/       # Données de démonstration
├── __init__.py
├── admin.py       # Configuration admin
├── apps.py        # Configuration de l'application
├── models.py      # Modèles
├── urls.py        # URLs du module
└── views.py       # Vues du module
```

## 📄 Licence

Ce projet est sous licence MIT.
