#!/bin/bash
set -euo pipefail

# Script de sauvegarde des données pour transfert entre machines

echo "🔧 Sauvegarde des données de l'application..."

# Choix de l'interpréteur Python
PYTHON_BIN="python3"
if [ -x "/home/zepe/Projets/projets_django/.venv/bin/python" ]; then
  PYTHON_BIN="/home/zepe/Projets/projets_django/.venv/bin/python"
elif [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
elif [ -x "venv/bin/python" ]; then
  PYTHON_BIN="venv/bin/python"
fi

# Créer le dossier de sauvegarde si inexistant
mkdir -p apps/utilisateurs/fixtures

echo "💾 Export des utilisateurs..."
"$PYTHON_BIN" manage.py dumpdata facturation.Utilisateur --indent 2 > apps/utilisateurs/fixtures/users.json

echo "💾 Export des articles..."
"$PYTHON_BIN" manage.py dumpdata facturation.Article --indent 2 > apps/utilisateurs/fixtures/articles.json

echo "💾 Export des clients..."
"$PYTHON_BIN" manage.py dumpdata facturation.Client --indent 2 > apps/utilisateurs/fixtures/clients.json

echo "💾 Export des factures..."
"$PYTHON_BIN" manage.py dumpdata facturation.Facture --indent 2 > apps/utilisateurs/fixtures/factures.json

echo "💾 Export des détails de factures..."
"$PYTHON_BIN" manage.py dumpdata facturation.DetailFacture --indent 2 > apps/utilisateurs/fixtures/details.json

echo ""
echo "✅ Sauvegarde terminée !"
echo ""
echo "Fichiers créés dans apps/utilisateurs/fixtures/:"
ls -lh apps/utilisateurs/fixtures/*.json
