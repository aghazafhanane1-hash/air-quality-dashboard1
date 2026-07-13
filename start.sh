#!/usr/bin/env bash
# Lance tout le pipeline en une seule commande : ./start.sh
set -e

cd "$(dirname "$0")/backend"

echo "-> Installation des dépendances..."
pip install -r requirements.txt --break-system-packages -q 2>/dev/null || pip install -r requirements.txt -q

echo "-> Collecte des données (API Open-Meteo)..."
python3 -m app.ingest || {
    echo "-> Collecte réelle indisponible, utilisation du jeu de données de démo..."
    python3 -m app.seed_demo_data
}

echo "-> Démarrage du serveur sur http://localhost:8000 ..."
echo "-> Ouvre maintenant frontend/index.html dans ton navigateur."
uvicorn app.main:app --port 8000
