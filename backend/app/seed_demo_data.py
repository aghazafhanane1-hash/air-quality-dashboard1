"""
Génère un jeu de données de démonstration réaliste et l'insère en base.

Ce script n'est PAS un substitut à la collecte réelle (app.ingest) : il sert
uniquement à peupler la base pour pouvoir démontrer/tester le tableau de bord
dans un environnement sans accès sortant à l'API Open-Meteo (ex: sandbox de
développement restreint). En conditions normales, utiliser `python -m
app.ingest` qui interroge la vraie API publique.

On simule volontairement quelques valeurs manquantes et une valeur aberrante
par ville, pour que le pipeline de nettoyage reste visiblement à l'oeuvre
même sur les données de démo.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.cleaner import clean_all
from app.config import CITIES
from app.storage import init_db, save_rows

random.seed(42)

BASE_LEVELS = {
    "pm10": 18,
    "pm2_5": 10,
    "carbon_monoxide": 200,
    "nitrogen_dioxide": 15,
    "ozone": 60,
    "european_aqi": 35,
}


def build_fake_raw_payload(hours: int = 120) -> dict:
    start = datetime(2026, 7, 6, 0, 0)
    times = [(start + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M") for h in range(hours)]

    hourly: dict[str, list] = {"time": times}
    for var, base in BASE_LEVELS.items():
        series = []
        for h in range(hours):
            # légère variation journalière + bruit
            diurnal = 1 + 0.3 * random.uniform(-1, 1)
            value = round(base * diurnal, 1)
            series.append(value)
        # injecte quelques valeurs manquantes (None) et une aberrante
        series[3] = None
        series[10] = -999  # valeur aberrante volontaire -> doit être filtrée au nettoyage
        hourly[var] = series

    return {"hourly": hourly}


def run() -> None:
    init_db()
    collected = [{"city": c["name"], "raw": build_fake_raw_payload()} for c in CITIES]
    rows = clean_all(collected)
    n = save_rows(rows)
    print(f"{n} lignes de démonstration insérées en base.")


if __name__ == "__main__":
    run()
