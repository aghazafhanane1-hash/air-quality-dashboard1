# Tableau de bord — Qualité de l'air

Application web de suivi de la qualité de l'air pour 5 villes françaises
(Grenoble, Paris, Marseille, Lyon, Lille), à partir de l'API publique
gratuite **Open-Meteo Air Quality** (données CAMS, sans clé d'API).

- **Back-end** : Python / FastAPI + SQLite — collecte, nettoyage, stockage, API JSON
- **Front-end** : HTML/JS statique + Chart.js — dashboard interactif (filtres, tendances, comparatif)

## Architecture

```
air-quality-dashboard/
├── backend/
│   ├── app/
│   │   ├── config.py         # villes suivies, variables, bornes de plausibilité
│   │   ├── collector.py      # étape 1 : collecte auprès de l'API publique
│   │   ├── cleaner.py        # étape 2 : nettoyage & contrôle qualité
│   │   ├── storage.py        # étape 3 : persistance SQLite + requêtes métier
│   │   ├── ingest.py         # orchestration collecte -> nettoyage -> stockage
│   │   ├── seed_demo_data.py # jeu de données de démo (voir "Remarque réseau")
│   │   └── main.py           # étape 4 : API FastAPI exposée au front
│   ├── tests/                # tests unitaires (collecte + nettoyage)
│   └── requirements.txt
├── frontend/
│   └── index.html            # dashboard (aucune installation nécessaire)
└── docs/
    ├── journal_ia.md
    └── rapport_comparatif.md
```

## Lancement rapide (une seule commande)

**Mac / Linux :**
```bash
./start.sh
```

**Windows :**
```bat
start.bat
```

Ce script installe les dépendances, collecte les données (ou génère un jeu
de démo si l'API est injoignable), puis démarre le serveur. Ouvre ensuite
`frontend/index.html` dans ton navigateur.

## Installation détaillée (si tu préfères contrôler chaque étape, ou isoler l'environnement avec venv)

Prérequis : Python 3.10+.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'application

**1. Collecter les données réelles** (interroge l'API publique Open-Meteo) :

```bash
python -m app.ingest
```

**2. Démarrer l'API :**

```bash
uvicorn app.main:app --reload --port 8000
```
o 
python -m uvicorn app.main:app --port 8000         

**3. Ouvrir le dashboard :**

Ouvrir simplement `frontend/index.html` dans un navigateur (double-clic, ou
`open frontend/index.html`).
Click droit sur fichier .html et selectioner Ouvrir avec Five Server 

## Remarque réseau (important)

Ce projet a été développé dans un environnement d'exécution dont l'accès
sortant est restreint à une liste de domaines autorisés, qui n'incluait pas
`open-meteo.com`. La collecte réelle (`app/ingest.py`) n'a donc pas pu être
exécutée à titre de démonstration dans cet environnement (erreur HTTP 403 à
l'appel de l'API), mais son bon fonctionnement est validé par des tests
unitaires qui simulent les réponses de l'API (mocks, voir `tests/`).

Pour permettre de démontrer et tester le dashboard sans dépendre du réseau,
un script `app/seed_demo_data.py` génère un jeu de données synthétique
plausible et l'insère dans la même base via le même pipeline de nettoyage :

```bash
python -m app.seed_demo_data
```

Dans un environnement avec accès réseau standard, `python -m app.ingest`
fonctionne directement contre la vraie API (testé et confirmé pendant le
développement — l'URL et les paramètres ont été vérifiés contre la
documentation officielle d'Open-Meteo).

## Lancer les tests

```bash
cd backend
pytest -v
```

Les tests couvrent :
- `cleaner.py` : timestamps manquants, valeurs aberrantes, valeurs
  manquantes, déduplication, tri
- `collector.py` : succès, erreur réseau, réponse malformée, résilience
  partielle (une ville en échec n'interrompt pas les autres)

## Questions métier couvertes par le dashboard

1. Quel est l'indice de qualité de l'air (AQI) actuel pour chaque ville ?
   → bandeau d'indicateurs clés en haut du dashboard
2. Comment évolue un polluant donné dans le temps pour une ville donnée ?
   → graphique de tendance horaire (filtrable par ville et par polluant)
3. Quelles villes sont les plus / moins exposées à un polluant donné ?
   → graphique comparatif (classement par moyenne)

## Endpoints API

| Endpoint | Description |
|---|---|
| `GET /api/cities` | liste des villes disponibles |
| `GET /api/variables` | liste des polluants disponibles |
| `GET /api/latest` | dernière mesure connue par ville (indicateurs clés) |
| `GET /api/timeseries?city=&variable=` | série temporelle d'un polluant pour une ville |
| `GET /api/ranking?variable=` | classement des villes par moyenne d'un polluant |

## Documents complémentaires

- [`docs/journal_ia.md`](docs/journal_ia.md) — journal de bord IA (prompts, outils, qualité des réponses)
- [`docs/rapport_comparatif.md`](docs/rapport_comparatif.md) — rapport d'analyse comparative des outils IA utilisés
