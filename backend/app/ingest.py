"""
Script d'orchestration : collecte -> nettoyage -> stockage.

Usage :
    python -m app.ingest

À lancer avant de démarrer l'API (ou à planifier régulièrement, ex. via cron,
pour tenir le tableau de bord à jour).
"""
from __future__ import annotations

import logging

from app.cleaner import clean_all
from app.collector import collect_all_cities
from app.config import CITIES
from app.storage import init_db, save_rows

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run() -> None:
    logger.info("Initialisation de la base...")
    init_db()

    logger.info("Collecte auprès d'Open-Meteo pour %d villes...", len(CITIES))
    collected = collect_all_cities(CITIES)
    logger.info("%d villes collectées avec succès", len(collected))

    logger.info("Nettoyage et contrôle qualité...")
    rows = clean_all(collected)
    logger.info("%d lignes propres obtenues", len(rows))

    n = save_rows(rows)
    logger.info("%d lignes écrites en base (%s)", n, "air_quality.db")


if __name__ == "__main__":
    run()
