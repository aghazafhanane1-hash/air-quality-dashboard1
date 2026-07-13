"""
Étape 2 - Nettoyage & contrôle qualité.

Transforme le JSON brut retourné par Open-Meteo (colonnes séparées, alignées
par index temporel) en une liste plate de mesures propres :
    {city, timestamp, pm10, pm2_5, carbon_monoxide, nitrogen_dioxide, ozone, european_aqi}

Règles appliquées :
- une ligne est rejetée si le timestamp est absent
- une valeur hors des bornes physiquement plausibles (PLAUSIBLE_RANGES) est
  considérée aberrante et remplacée par None (valeur manquante), plutôt que
  de fausser les statistiques ou les graphiques
- une ligne où TOUTES les variables sont manquantes est rejetée (elle n'a
  aucune valeur exploitable)
- les lignes sont triées par timestamp croissant
- les doublons (même ville + même timestamp) sont supprimés, en gardant la
  première occurrence
"""
from __future__ import annotations

from typing import Any

from app.config import AIR_QUALITY_VARIABLES, PLAUSIBLE_RANGES


def _is_plausible(variable: str, value: Any) -> bool:
    if value is None:
        return False
    low, high = PLAUSIBLE_RANGES.get(variable, (float("-inf"), float("inf")))
    return low <= value <= high


def clean_city_payload(city_name: str, raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Nettoie le payload brut d'une seule ville et renvoie des lignes plates."""
    hourly = raw_payload.get("hourly", {})
    timestamps = hourly.get("time", [])

    rows: list[dict[str, Any]] = []
    for i, ts in enumerate(timestamps):
        if not ts:
            continue  # timestamp manquant : ligne inexploitable

        row: dict[str, Any] = {"city": city_name, "timestamp": ts}
        has_value = False
        for var in AIR_QUALITY_VARIABLES:
            series = hourly.get(var, [])
            value = series[i] if i < len(series) else None
            if _is_plausible(var, value):
                row[var] = float(value)
                has_value = True
            else:
                row[var] = None  # valeur manquante ou aberrante -> normalisée à None

        if has_value:
            rows.append(row)

    return rows


def clean_all(collected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Nettoie les payloads de toutes les villes, déduplique et trie."""
    all_rows: list[dict[str, Any]] = []
    for entry in collected:
        all_rows.extend(clean_city_payload(entry["city"], entry["raw"]))

    # Déduplication (ville, timestamp), on garde la première occurrence
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for row in all_rows:
        key = (row["city"], row["timestamp"])
        if key not in seen:
            seen.add(key)
            deduped.append(row)

    deduped.sort(key=lambda r: (r["city"], r["timestamp"]))
    return deduped
