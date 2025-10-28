#!/bin/bash
# DNA-Sec - Script de demarrage rapide pour Linux/macOS
# Script pour lancer facilement l'interface web

set -e  # Quitter en cas d'erreur

echo "DNA-Sec - Demarrage de l'interface web"
echo ""

# Verifier si dans le bon dossier
if [ ! -f "web/app_demo.py" ]; then
    echo "[ERREUR] Executez ce script depuis le dossier racine DNA/"
    exit 1
fi

# Verifier Python
echo "Verification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python 3 n'est pas installe"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "[OK] $PYTHON_VERSION"

# Installer les dependances si necessaire
echo ""
echo "Verification des dependances..."

if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installation de Flask..."
    pip3 install flask werkzeug
fi

if ! python3 -c "import Bio" 2>/dev/null; then
    echo "Installation des dependances..."
    pip3 install -r requirements.txt
fi

echo "[OK] Dependances OK"

# Choisir le mode
echo ""
echo "Choisissez le mode de demarrage:"
echo "  1. Mode DEMO (sans YARA) - Recommande pour les tests"
echo "  2. Mode COMPLET (avec YARA) - Necessite YARA installe"
echo ""
read -p "Votre choix (1 ou 2): " choice

if [ "$choice" = "2" ]; then
    # Verifier si YARA est installe
    if ! python3 -c "import yara" 2>/dev/null; then
        echo ""
        echo "[ATTENTION] YARA n'est pas installe ou mal configure"
        echo "   Consultez docs/INSTALL_YARA.md pour l'installation"
        echo ""
        echo "   Basculement sur le mode DEMO..."
        sleep 2
        APP_FILE="app_demo.py"
    else
        APP_FILE="app.py"
    fi
else
    APP_FILE="app_demo.py"
fi

# Demarrer le serveur
echo ""
echo "Demarrage du serveur web..."
echo "   URL: http://localhost:5000"
echo ""
echo "   Appuyez sur Ctrl+C pour arreter"
echo ""

cd web
python3 $APP_FILE
