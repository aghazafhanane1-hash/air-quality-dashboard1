@echo off
REM Lance tout le pipeline en une seule commande : start.bat
cd /d "%~dp0backend"

echo -^> Installation des dependances...
pip install -r requirements.txt

echo -^> Collecte des donnees (API Open-Meteo)...
python -m app.ingest
if errorlevel 1 (
    echo -^> Collecte reelle indisponible, utilisation du jeu de donnees de demo...
    python -m app.seed_demo_data
)

echo -^> Demarrage du serveur sur http://localhost:8000 ...
echo -^> Ouvre maintenant frontend\index.html dans ton navigateur.
uvicorn app.main:app --port 8000
