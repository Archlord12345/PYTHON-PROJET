#!/bin/bash
# Script de sauvegarde des données pour transfert entre machines

echo "🔧 Sauvegarde des données de l'application..."

# Activer l'environnement virtuel
source venv/bin/activate

# Créer le dossier de sauvegarde si inexistant
mkdir -p apps/utilisateurs/fixtures

echo "💾 Export des utilisateurs..."
python manage.py dumpdata facturation.Utilisateur --indent 2 > apps/utilisateurs/fixtures/users.json

echo "💾 Export des articles..."
python manage.py dumpdata facturation.Article --indent 2 > apps/utilisateurs/fixtures/articles.json

echo "💾 Export des clients..."
python manage.py dumpdata facturation.Client --indent 2 > apps/utilisateurs/fixtures/clients.json

echo "💾 Export des factures..."
python manage.py dumpdata facturation.Facture --indent 2 > apps/utilisateurs/fixtures/factures.json

echo "💾 Export des détails de factures..."
python manage.py dumpdata facturation.DetailFacture --indent 2 > apps/utilisateurs/fixtures/details.json

echo ""
echo "✅ Sauvegarde terminée !"
echo ""
echo "Fichiers créés dans apps/utilisateurs/fixtures/:"
ls -lh apps/utilisateurs/fixtures/*.json
echo ""
echo "📋 Pour restaurer sur une nouvelle machine :"
echo "   python manage.py loaddata apps/utilisateurs/fixtures/users.json"
echo "   python manage.py loaddata apps/utilisateurs/fixtures/articles.json"
echo "   python manage.py loaddata apps/utilisateurs/fixtures/clients.json"
echo "   python manage.py loaddata apps/utilisateurs/fixtures/factures.json"
echo "   python manage.py loaddata apps/utilisateurs/fixtures/details.json"
