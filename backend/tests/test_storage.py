"""
Tests unitaires du module storage.py.

Généré initialement par Gemini (voir docs/journal_ia.md, étape 8), puis
corrigé après détection de 3 bugs à l'exécution :
  1. import placeholder jamais remplacé (`from ton_module import ...`)
  2. fixture `db_path = ":memory:"` incompatible avec l'architecture de
     storage.py (chaque fonction ouvre sa propre connexion SQLite via
     get_connection() -> une base en mémoire ne persiste pas entre appels)
  3. assertion cassée, toujours vraie quelle que soit la valeur testée
La version brute générée par Gemini (avec les 3 bugs encore présents) est
conservée à titre d'illustration dans backend/test_storage_gemini.py.
"""
import tempfile
import os

import pytest

from app.storage import (
    init_db,
    save_rows,
    get_timeseries,
    get_latest_by_city,
    get_city_ranking,
    list_cities,
    get_connection,
)
from app.config import AIR_QUALITY_VARIABLES


@pytest.fixture
def db_path():
    """Fichier SQLite temporaire réel, partagé entre les appels du test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    os.remove(path)


def test_init_db(db_path):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='air_quality_measurements'"
        )
        assert cur.fetchone() is not None


def test_save_rows_empty(db_path):
    assert save_rows([], db_path=db_path) == 0


def test_save_rows_and_list_cities(db_path):
    var_data = {var: 10.5 for var in AIR_QUALITY_VARIABLES}
    rows = [
        {"city": "Paris", "timestamp": "2026-07-13T10:00:00", **var_data},
        {"city": "Lyon", "timestamp": "2026-07-13T10:00:00", **var_data},
    ]
    nb_inserted = save_rows(rows, db_path=db_path)
    assert nb_inserted == 2
    assert list_cities(db_path=db_path) == ["Lyon", "Paris"]


def test_save_rows_replace(db_path):
    if not AIR_QUALITY_VARIABLES:
        pytest.skip("AIR_QUALITY_VARIABLES est vide")
    v = AIR_QUALITY_VARIABLES[0]
    row1 = {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 20.0}
    row2 = {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 35.5}
    save_rows([row1], db_path=db_path)
    save_rows([row2], db_path=db_path)
    timeseries = get_timeseries("Paris", v, db_path=db_path)
    assert len(timeseries) == 1
    assert timeseries[0]["value"] == 35.5


def test_get_timeseries(db_path):
    if not AIR_QUALITY_VARIABLES:
        pytest.skip("AIR_QUALITY_VARIABLES est vide")
    v = AIR_QUALITY_VARIABLES[0]
    rows = [
        {"city": "Paris", "timestamp": "2026-07-13T12:00:00", v: 15.0},
        {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 10.0},
        {"city": "Lyon", "timestamp": "2026-07-13T11:00:00", v: 99.0},
    ]
    save_rows(rows, db_path=db_path)
    series = get_timeseries("Paris", v, db_path=db_path)
    assert len(series) == 2
    assert series[0]["timestamp"] == "2026-07-13T10:00:00"
    assert series[0]["value"] == 10.0
    assert series[1]["timestamp"] == "2026-07-13T12:00:00"
    assert series[1]["value"] == 15.0


def test_get_timeseries_invalid_variable(db_path):
    with pytest.raises(ValueError, match="Variable inconnue"):
        get_timeseries("Paris", "variable_inexistante", db_path=db_path)


def test_get_latest_by_city(db_path):
    if not AIR_QUALITY_VARIABLES:
        pytest.skip("AIR_QUALITY_VARIABLES est vide")
    v = AIR_QUALITY_VARIABLES[0]
    rows = [
        {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 10.0},
        {"city": "Paris", "timestamp": "2026-07-13T11:00:00", v: 20.0},
        {"city": "Lyon", "timestamp": "2026-07-13T09:00:00", v: 5.0},
    ]
    save_rows(rows, db_path=db_path)
    latest = get_latest_by_city(db_path=db_path)
    assert len(latest) == 2
    # Trié par ville (Lyon puis Paris)
    assert latest[0]["city"] == "Lyon"
    assert latest[0]["timestamp"] == "2026-07-13T09:00:00"  # comparaison réelle, corrigée
    paris_data = next(item for item in latest if item["city"] == "Paris")
    assert paris_data["timestamp"] == "2026-07-13T11:00:00"
    assert paris_data[v] == 20.0


def test_get_city_ranking(db_path):
    if not AIR_QUALITY_VARIABLES:
        pytest.skip("AIR_QUALITY_VARIABLES est vide")
    v = AIR_QUALITY_VARIABLES[0]
    rows = [
        {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 10.0},
        {"city": "Paris", "timestamp": "2026-07-13T11:00:00", v: 20.0},
        {"city": "Lyon", "timestamp": "2026-07-13T10:00:00", v: 40.0},
        {"city": "Lyon", "timestamp": "2026-07-13T11:00:00", v: None},
        {"city": "Marseille", "timestamp": "2026-07-13T10:00:00", v: 5.0},
    ]
    save_rows(rows, db_path=db_path)
    ranking = get_city_ranking(v, db_path=db_path)
    assert len(ranking) == 3
    assert ranking[0]["city"] == "Lyon"
    assert ranking[0]["average"] == 40.0
    assert ranking[0]["n_samples"] == 1
    assert ranking[1]["city"] == "Paris"
    assert ranking[1]["average"] == 15.0
    assert ranking[1]["n_samples"] == 2
    assert ranking[2]["city"] == "Marseille"


def test_get_city_ranking_invalid_variable(db_path):
    with pytest.raises(ValueError, match="Variable inconnue"):
        get_city_ranking("variable_inexistante", db_path=db_path)
