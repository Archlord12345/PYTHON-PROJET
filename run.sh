#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour arrêter les processus en arrière-plan à la sortie
cleanup() {
    echo -e "\n${BLUE}Arrêt des processus en cours...${NC}"
    kill $SERVER_PID $TAILWIND_PID 2>/dev/null
    exit 0
}

# Capturer le signal d'interruption (Ctrl+C)
trap cleanup INT

# Lancer le serveur Django en arrière-plan
echo -e "${GREEN}Démarrage du serveur Django...${NC}"
python manage.py runserver &
SERVER_PID=$!

# Donner un peu de temps au serveur pour démarrer
sleep 2

# Lancer Tailwind en arrière-plan
echo -e "\n${GREEN}Démarrage de Tailwind CSS...${NC}"
python manage.py tailwind start &
TAILWIND_PID=$!

echo -e "\n${BLUE}Serveur Django et Tailwind démarrés avec succès !${NC}"
echo -e "${BLUE}Appuyez sur Ctrl+C pour arrêter les serveurs.${NC}"

# Attendre indéfiniment
wait $SERVER_PID $TAILWIND_PID