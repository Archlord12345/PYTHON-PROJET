#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Initialisation des variables
SERVER_PID=""
TAILWIND_PID=""
MIGRATION_PID=""

# Fonction pour afficher un message d'information
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Fonction pour afficher un message de succès
success() {
    echo -e "${GREEN}[SUCCÈS]${NC} $1"
}

# Fonction pour afficher un message d'avertissement
warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

# Fonction pour afficher un message d'erreur et quitter
error() {
    echo -e "${RED}[ERREUR]${NC} $1"
    exit 1
}

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Fonction pour arrêter les processus en arrière-plan à la sortie
cleanup() {
    info "Nettoyage des processus en cours..."
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || warning "Impossible d'arrêter le serveur Django (PID: $SERVER_PID)"
    fi
    if [ -n "$TAILWIND_PID" ]; then
        kill $TAILWIND_PID 2>/dev/null || warning "Impossible d'arrêter Tailwind (PID: $TAILWIND_PID)"
    fi
    if [ -n "$MIGRATION_PID" ]; then
        wait $MIGRATION_PID 2>/dev/null
    fi
    exit 0
}

# Capturer les signaux d'arrêt
trap cleanup INT TERM EXIT

# Vérifier les dépendances
if ! command_exists python3; then
    error "Python 3 n'est pas installé. Veuillez l'installer avant de continuer."
fi

# Vérifier si manage.py existe
if [ ! -f "manage.py" ]; then
    error "Le fichier manage.py est introuvable. Assurez-vous d'exécuter ce script depuis le répertoire racine du projet."
fi

# Lancer les migrations en arrière-plan
info "Application des migrations de base de données..."
python3 manage.py makemigrations && python3 manage.py migrate &
MIGRATION_PID=$!

# Attendre que les migrations soient terminées avant de démarrer le serveur
wait $MIGRATION_PID
if [ $? -ne 0 ]; then
    error "Les migrations ont échoué. Veuillez corriger les erreurs avant de continuer."
fi
success "Migrations appliquées avec succès"

# Démarrer le serveur Django en arrière-plan
info "Démarrage du serveur Django..."
python3 manage.py runserver &
SERVER_PID=$!

# Vérifier que le serveur a démarré
sleep 2
if ! ps -p $SERVER_PID > /dev/null; then
    error "Le serveur Django n'a pas pu démarrer. Vérifiez les logs pour plus d'informations."
fi
success "Serveur Django démarré avec succès (PID: $SERVER_PID)"

# Compiler et démarrer Tailwind CSS si le dossier tailwind est présent
if [ -d "theme/static_src" ]; then
    info "Compilation de Tailwind CSS..."
    python3 manage.py tailwind build &
    TAILWIND_PID=$!
    wait $TAILWIND_PID
    
    if [ $? -eq 0 ]; then
        success "Compilation de Tailwind CSS terminée"
        info "Démarrage du watcher Tailwind CSS..."
        python3 manage.py tailwind start &
        TAILWIND_PID=$!
        success "Watcher Tailwind CSS démarré (PID: $TAILWIND_PID)"
    else
        warning "Échec de la compilation de Tailwind CSS. Vérifiez les dépendances."
    fi
else
    warning "Dossier theme/static_src introuvable. Ignorant la compilation Tailwind CSS."
fi

echo -e "\n${GREEN}=== Application prête ! ===${NC}"
echo -e "${BLUE}Serveur Django en cours d'exécution (PID: ${SERVER_PID})${NC}"
[ -n "$TAILWIND_PID" ] && echo -e "${BLUE}Watcher Tailwind CSS en cours d'exécution (PID: ${TAILWIND_PID})${NC}"
echo -e "${BLUE}Appuyez sur Ctrl+C pour arrêter les serveurs.${NC}"

# Attendre que tous les processus en arrière-plan se terminent
wait