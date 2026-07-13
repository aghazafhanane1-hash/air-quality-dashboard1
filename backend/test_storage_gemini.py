import pytest
import sqlite3
from unittest.mock import patch

# Remplacer 'ton_module' par le nom réel de ton fichier/module Python
from ton_module import (
    init_db,
    save_rows,
    get_timeseries,
    get_latest_by_city,
    get_city_ranking,
    list_cities,
    get_connection,
)

# On suppose que AIR_QUALITY_VARIABLES contient par exemple ["pm10", "pm25", "no2"]
# Si besoin, tu peux patcher la config, mais ici on va utiliser les variables réelles de ton app.
from app.config import AIR_QUALITY_VARIABLES


@pytest.fixture
def db_mem():
    """Fixture qui initialise une base SQLite en mémoire et la nettoie après le test."""
    db_path = ":memory:"
    init_db(db_path)
    return db_path


def test_init_db(db_mem):
    """Vérifie que la table est correctement créée avec le bon schéma."""
    with get_connection(db_mem) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='air_quality_measurements'")
        assert cur.fetchone() is not None


def test_save_rows_empty(db_mem):
    """Vérifie que l'insertion d'une liste vide renvoie 0 et ne plante pas."""
    assert save_rows([], db_path=db_mem) == 0


def test_save_rows_and_list_cities(db_mem):
    """Vérifie l'insertion de données et la récupération de la liste des villes."""
    # On dynamise la création des données de test selon tes AIR_QUALITY_VARIABLES
    var_data = {var: 10.5 for var in AIR_QUALITY_VARIABLES}
    
    rows = [
        {"city": "Paris", "timestamp": "2026-07-13T10:00:00", **var_data},
        {"city": "Lyon", "timestamp": "2026-07-13T10:00:00", **var_data},
    ]
    
    nb_inserted = save_rows(rows, db_path=db_mem)
    assert nb_inserted == 2
    
    cities = list_cities(db_path=db_mem)
    assert cities == ["Lyon", "Paris"]  # Trié par ordre alphabétique


def test_save_rows_replace(db_mem):
    """Vérifie que 'INSERT OR REPLACE' fonctionne bien sur la clé primaire (city, timestamp)."""
    if not AIR_QUALITY_VARIABLES:
        pytest.skip("AIR_QUALITY_VARIABLES est vide")
        
    v = AIR_QUALITY_VARIABLES[0]
    
    row1 = {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 20.0}
    row2 = {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 35.5} # Même clé, valeur différente
    
    save_rows([row1], db_path=db_mem)
    save_rows([row2], db_path=db_mem)
    
    # On vérifie qu'il n'y a qu'une seule ligne et qu'elle a été mise à jour
    timeseries = get_timeseries("Paris", v, db_path=db_mem)
    assert len(timeseries) == 1
    assert timeseries[0]["value"] == 35.5


def test_get_timeseries(db_mem):
    """Vérifie la récupération d'une série temporelle triée par timestamp."""
    if not AIR_QUALITY_VARIABLES:
        pytest.skip("AIR_QUALITY_VARIABLES est vide")
        
    v = AIR_QUALITY_VARIABLES[0]
    
    rows = [
        {"city": "Paris", "timestamp": "2026-07-13T12:00:00", v: 15.0},
        {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 10.0},  # Inséré après mais chronologiquement avant
        {"city": "Lyon", "timestamp": "2026-07-13T11:00:00", v: 99.0},   # Autre ville
    ]
    save_rows(rows, db_path=db_mem)
    
    series = get_timeseries("Paris", v, db_path=db_mem)
    
    assert len(series) == 2
    assert series[0]["timestamp"] == "2026-07-13T10:00:00"
    assert series[0]["value"] == 10.0
    assert series[1]["timestamp"] == "2026-07-13T12:00:00"
    assert series[1]["value"] == 15.0


def test_get_timeseries_invalid_variable(db_mem):
    """Vérifie qu'une erreur est levée si la variable demandée n'existe pas."""
    with pytest.raises(ValueError, match="Variable inconnue"):
        get_timeseries("Paris", "variable_inexistante", db_path=db_mem)


def test_get_latest_by_city(db_mem):
    """Vérifie qu'on récupère uniquement le dernier point de mesure pour chaque ville."""
    if not AIR_QUALITY_VARIABLES:
        pytest.skip("AIR_QUALITY_VARIABLES est vide")
        
    v = AIR_QUALITY_VARIABLES[0]
    
    rows = [
        {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 10.0},
        {"city": "Paris", "timestamp": "2026-07-13T11:00:00", v: 20.0},  # Le plus récent pour Paris
        {"city": "Lyon", "timestamp": "2026-07-13T09:00:00", v: 5.0},   # Le plus récent pour Lyon
    ]
    save_rows(rows, db_path=db_mem)
    
    latest = get_latest_by_city(db_path=db_mem)
    
    assert len(latest) == 2
    # Trié par ville normalement (Lyon puis Paris)
    assert latest[0]["city"] == "Lyon"
    assert latest[0]["timestamp"] == "2026-07-09:00:00" if "09:00:00" in latest[0]["timestamp"] else True
    
    paris_data = next(item for item in latest if item["city"] == "Paris")
    assert paris_data["timestamp"] == "2026-07-13T11:00:00"
    assert paris_data[v] == 20.0


def test_get_city_ranking(db_mem):
    """Vérifie le classement des villes par moyenne décroissante (ignorant les NULL)."""
    if not AIR_QUALITY_VARIABLES:
        pytest.skip("AIR_QUALITY_VARIABLES est vide")
        
    v = AIR_QUALITY_VARIABLES[0]
    
    rows = [
        {"city": "Paris", "timestamp": "2026-07-13T10:00:00", v: 10.0},
        {"city": "Paris", "timestamp": "2026-07-13T11:00:00", v: 20.0},  # Moyenne Paris = 15.0
        
        {"city": "Lyon", "timestamp": "2026-07-13T10:00:00", v: 40.0},
        {"city": "Lyon", "timestamp": "2026-07-13T11:00:00", v: None},   # Ce NULL doit être ignoré, Moyenne Lyon = 40.0
        
        {"city": "Marseille", "timestamp": "2026-07-13T10:00:00", v: 5.0}, # Moyenne Marseille = 5.0
    ]
    save_rows(rows, db_path=db_mem)
    
    ranking = get_city_ranking(v, db_path=db_mem)
    
    assert len(ranking) == 3
    # Ordre attendu (DESC) : Lyon (40), Paris (15), Marseille (5)
    assert ranking[0]["city"] == "Lyon"
    assert ranking[0]["average"] == 40.0
    assert ranking[0]["n_samples"] == 1  # Le None n'est pas compté
    
    assert ranking[1]["city"] == "Paris"
    assert ranking[1]["average"] == 15.0
    assert ranking[1]["n_samples"] == 2
    
    assert ranking[2]["city"] == "Marseille"


def test_get_city_ranking_invalid_variable(db_mem):
    """Vérifie qu'une erreur est levée si on demande le classement d'une fausse variable."""
    with pytest.raises(ValueError, match="Variable inconnue"):
        get_city_ranking("variable_inexistante", db_path=db_mem)