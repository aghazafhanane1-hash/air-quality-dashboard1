"""
Étape 3 - Stockage & exploitation.

Persistance dans SQLite (fichier unique, zéro configuration - suffisant pour
ce volume de données et facile à lancer sans serveur externe) et fonctions de
requêtage répondant aux questions métier du tableau de bord :
- dernières valeurs / indicateurs clés par ville
- série temporelle d'un polluant pour une ville
- classement des villes par polluant moyen (pour le comparatif)
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from app.config import AIR_QUALITY_VARIABLES, DB_PATH

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS air_quality_measurements (
    city TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    {", ".join(f"{var} REAL" for var in AIR_QUALITY_VARIABLES)},
    PRIMARY KEY (city, timestamp)
);
"""


@contextmanager
def get_connection(db_path: str = DB_PATH) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute(SCHEMA)
        conn.commit()


def save_rows(rows: list[dict[str, Any]], db_path: str = DB_PATH) -> int:
    """Insère (ou remplace) les lignes nettoyées. Renvoie le nombre de lignes écrites."""
    if not rows:
        return 0
    columns = ["city", "timestamp"] + AIR_QUALITY_VARIABLES
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT OR REPLACE INTO air_quality_measurements ({', '.join(columns)}) VALUES ({placeholders})"

    with get_connection(db_path) as conn:
        conn.executemany(sql, [tuple(row.get(col) for col in columns) for row in rows])
        conn.commit()
    return len(rows)


def get_timeseries(city: str, variable: str, db_path: str = DB_PATH) -> list[dict[str, Any]]:
    if variable not in AIR_QUALITY_VARIABLES:
        raise ValueError(f"Variable inconnue: {variable}")
    with get_connection(db_path) as conn:
        cur = conn.execute(
            f"SELECT timestamp, {variable} AS value FROM air_quality_measurements "
            "WHERE city = ? ORDER BY timestamp ASC",
            (city,),
        )
        return [dict(r) for r in cur.fetchall()]


def get_latest_by_city(db_path: str = DB_PATH) -> list[dict[str, Any]]:
    """Dernier point de mesure disponible pour chaque ville (indicateurs clés)."""
    with get_connection(db_path) as conn:
        cols = ", ".join(AIR_QUALITY_VARIABLES)
        cur = conn.execute(
            f"""
            SELECT m.city, m.timestamp, {cols}
            FROM air_quality_measurements m
            INNER JOIN (
                SELECT city, MAX(timestamp) AS max_ts
                FROM air_quality_measurements
                GROUP BY city
            ) latest ON m.city = latest.city AND m.timestamp = latest.max_ts
            ORDER BY m.city
            """
        )
        return [dict(r) for r in cur.fetchall()]


def get_city_ranking(variable: str, db_path: str = DB_PATH) -> list[dict[str, Any]]:
    """Classe les villes par moyenne d'un polluant, ignorant les NULL."""
    if variable not in AIR_QUALITY_VARIABLES:
        raise ValueError(f"Variable inconnue: {variable}")
    with get_connection(db_path) as conn:
        cur = conn.execute(
            f"""
            SELECT city, AVG({variable}) AS average, COUNT({variable}) AS n_samples
            FROM air_quality_measurements
            WHERE {variable} IS NOT NULL
            GROUP BY city
            ORDER BY average DESC
            """
        )
        return [dict(r) for r in cur.fetchall()]


def list_cities(db_path: str = DB_PATH) -> list[str]:
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT DISTINCT city FROM air_quality_measurements ORDER BY city")
        return [r["city"] for r in cur.fetchall()]
