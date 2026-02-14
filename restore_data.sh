#!/bin/bash
set -euo pipefail

# Script de restauration des fixtures

echo "🔄 Restauration des données de l'application..."

if [ ! -f "manage.py" ]; then
  echo "❌ manage.py introuvable. Lance le script depuis la racine du projet."
  exit 1
fi

# Choix de l'interpréteur Python
PYTHON_BIN="python3"
if [ -x "/home/zepe/Projets/projets_django/.venv/bin/python" ]; then
  PYTHON_BIN="/home/zepe/Projets/projets_django/.venv/bin/python"
elif [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
elif [ -x "venv/bin/python" ]; then
  PYTHON_BIN="venv/bin/python"
fi

echo "🧱 Application des migrations..."
"$PYTHON_BIN" manage.py migrate

echo "📥 Chargement des utilisateurs..."
"$PYTHON_BIN" manage.py loaddata apps/utilisateurs/fixtures/users.json

echo "📥 Chargement des articles..."
"$PYTHON_BIN" manage.py loaddata apps/utilisateurs/fixtures/articles.json

echo "📥 Chargement des clients..."
"$PYTHON_BIN" manage.py loaddata apps/utilisateurs/fixtures/clients.json

echo "📥 Chargement des factures..."
"$PYTHON_BIN" manage.py loaddata apps/utilisateurs/fixtures/factures.json

echo "📥 Chargement des détails de factures..."
"$PYTHON_BIN" manage.py loaddata apps/utilisateurs/fixtures/details.json

echo ""
echo "✅ Restauration terminée."
