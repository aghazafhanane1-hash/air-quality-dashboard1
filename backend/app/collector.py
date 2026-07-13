"""
Étape 1 - Collecte.

Interroge l'API publique Open-Meteo Air Quality (gratuite, sans clé) pour
récupérer les mesures horaires de pollution de chaque ville suivie.

La fonction est volontairement séparée du nettoyage (cf. cleaner.py) et du
stockage (cf. storage.py) pour rester testable indépendamment.
"""
from __future__ import annotations

import logging
from typing import Any

import requests

from app.config import (
    AIR_QUALITY_VARIABLES,
    OPEN_METEO_AIR_QUALITY_URL,
    PAST_DAYS,
)

logger = logging.getLogger(__name__)


class CollectorError(Exception):
    """Erreur lors de la collecte auprès de l'API publique."""


def fetch_city_air_quality(
    lat: float, lon: float, timeout: int = 15
) -> dict[str, Any]:
    """
    Récupère les données brutes (JSON) pour une position géographique donnée.

    Lève CollectorError en cas d'échec réseau, de timeout ou de réponse HTTP
    en erreur, afin que l'appelant puisse décider comment réagir (retry,
    log, arrêt) sans avoir à connaître les détails de `requests`.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(AIR_QUALITY_VARIABLES),
        "past_days": PAST_DAYS,
        "forecast_days": 1,
        "timezone": "auto",
    }
    try:
        response = requests.get(OPEN_METEO_AIR_QUALITY_URL, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("Échec de la collecte pour (%s, %s): %s", lat, lon, exc)
        raise CollectorError(f"Impossible de contacter l'API Open-Meteo: {exc}") from exc

    data = response.json()
    if "hourly" not in data:
        raise CollectorError(f"Réponse API inattendue (pas de champ 'hourly'): {data}")
    return data


def collect_all_cities(cities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Collecte les données pour une liste de villes.

    Une ville en échec n'interrompt pas la collecte des autres : on journalise
    l'erreur et on continue (la source publique est régulièrement instable
    pour certaines communes / coordonnées).
    """
    results = []
    for city in cities:
        try:
            raw = fetch_city_air_quality(city["lat"], city["lon"])
            results.append({"city": city["name"], "raw": raw})
        except CollectorError as exc:
            logger.warning("Ville ignorée (%s): %s", city["name"], exc)
    return results
