# Transfert de données entre machines

Ce dossier contient toutes les données de la base pour faciliter le transfert entre machines.

## Fichiers de données (Fixtures)

- `users.json` - Utilisateurs (comptes gestionnaire et caissier)
- `articles.json` - Tous les articles du catalogue
- `clients.json` - Tous les clients
- `factures.json` - Toutes les factures
- `details.json` - Détails des factures

## Comment transférer vers une nouvelle machine

### 1. Copier les fichiers
Copier tout le dossier `/apps/utilisateurs/fixtures/` vers la nouvelle machine.

### 2. Charger les données
Sur la nouvelle machine, après avoir configuré la base de données PostgreSQL :

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Créer la base de données et les tables
python manage.py migrate

# Charger les données
cd apps/utilisateurs/fixtures

# Charger les utilisateurs
python manage.py loaddata users.json

# Charger les articles
python manage.py loaddata articles.json

# Charger les clients
python manage.py loaddata clients.json

# Charger les factures
python manage.py loaddata factures.json

# Charger les détails de factures
python manage.py loaddata details.json
```

### 3. Identifiants par défaut après transfert

| Login | Mot de passe | Rôle |
|-------|--------------|------|
| `gestionnaire2` | `admin` | Gestionnaire |
| `gestionnaire` | `gestionnaire` | Gestionnaire |
| `caissiere` | `caissiere` | Caissier |

## Créer une nouvelle sauvegarde

Pour mettre à jour les fixtures avec les dernières données :

```bash
source venv/bin/activate

cd apps/utilisateurs/fixtures

python manage.py dumpdata facturation.Utilisateur --indent 2 > users.json
python manage.py dumpdata facturation.Article --indent 2 > articles.json
python manage.py dumpdata facturation.Client --indent 2 > clients.json
python manage.py dumpdata facturation.Facture --indent 2 > factures.json
python manage.py dumpdata facturation.DetailFacture --indent 2 > details.json
```

## Sauvegarde complète de la base (option avancée)

Pour une sauvegarde complète en une seule commande :

```bash
# Sauvegarder tout
python manage.py dumpdata facturation --indent 2 > backup_complete.json

# Restaurer tout
python manage.py loaddata backup_complete.json
```

## Note importante

Les mots de passe dans les fixtures sont **hashés**. Tu peux les utiliser directement après le transfert sans modification.
