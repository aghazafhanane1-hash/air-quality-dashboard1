"""
Étape 4 - Restitution (API).

Expose les données stockées en SQLite au format JSON pour le tableau de bord
front-end. Le front est un fichier statique servi séparément (voir README) ;
CORS est donc ouvert pour simplifier le lancement en local.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import AIR_QUALITY_VARIABLES, CITIES
from app.storage import get_city_ranking, get_latest_by_city, get_timeseries, init_db, list_cities

app = FastAPI(title="Tableau de bord Qualité de l'Air", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/cities")
def cities() -> list[str]:
    stored = list_cities()
    return stored if stored else [c["name"] for c in CITIES]


@app.get("/api/variables")
def variables() -> list[str]:
    return AIR_QUALITY_VARIABLES


@app.get("/api/latest")
def latest() -> list[dict]:
    """Indicateurs clés (dernière mesure connue) pour chaque ville."""
    return get_latest_by_city()


@app.get("/api/timeseries")
def timeseries(
    city: str = Query(..., description="Nom de la ville"),
    variable: str = Query("pm2_5", description="Variable à tracer"),
) -> list[dict]:
    """Série temporelle d'un polluant pour une ville (pour le graphique de tendance)."""
    if variable not in AIR_QUALITY_VARIABLES:
        raise HTTPException(400, f"Variable inconnue: {variable}")
    return get_timeseries(city, variable)


@app.get("/api/ranking")
def ranking(variable: str = Query("pm2_5")) -> list[dict]:
    """Classement des villes par moyenne d'un polluant (pour le graphique comparatif)."""
    if variable not in AIR_QUALITY_VARIABLES:
        raise HTTPException(400, f"Variable inconnue: {variable}")
    return get_city_ranking(variable)
