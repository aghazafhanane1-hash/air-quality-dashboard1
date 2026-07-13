"""
Configuration centrale de l'application.

On suit un panel fixe de villes françaises. Chaque ville est définie par ses
coordonnées (l'API Open-Meteo attend latitude/longitude, pas de nom de ville).
"""

CITIES = [
    {"name": "Grenoble", "lat": 45.1885, "lon": 5.7245},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Marseille", "lat": 43.2965, "lon": 5.3698},
    {"name": "Lyon", "lat": 45.7640, "lon": 4.8357},
    {"name": "Lille", "lat": 50.6292, "lon": 3.0573},
]

# Variables demandées à l'API Open-Meteo Air Quality
AIR_QUALITY_VARIABLES = [
    "pm10",
    "pm2_5",
    "carbon_monoxide",
    "nitrogen_dioxide",
    "ozone",
    "european_aqi",
]

OPEN_METEO_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# Nombre de jours d'historique récupérés à chaque collecte
PAST_DAYS = 5

DB_PATH = "air_quality.db"

# Bornes physiquement plausibles utilisées pour détecter les valeurs aberrantes
# (au-delà, on considère la mesure comme un défaut de capteur / de transmission)
PLAUSIBLE_RANGES = {
    "pm10": (0, 1000),
    "pm2_5": (0, 1000),
    "carbon_monoxide": (0, 50000),
    "nitrogen_dioxide": (0, 1000),
    "ozone": (0, 1000),
    "european_aqi": (0, 500),
}
