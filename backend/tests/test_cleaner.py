from app.cleaner import clean_all, clean_city_payload


def make_payload(times, pm10=None, pm2_5=None):
    n = len(times)
    pm10 = pm10 or [10.0] * n
    pm2_5 = pm2_5 or [5.0] * n
    return {
        "hourly": {
            "time": times,
            "pm10": pm10,
            "pm2_5": pm2_5,
            "carbon_monoxide": [100.0] * n,
            "nitrogen_dioxide": [20.0] * n,
            "ozone": [30.0] * n,
            "european_aqi": [40.0] * n,
        }
    }


def test_clean_city_payload_basic_row():
    payload = make_payload(["2026-07-01T00:00"])
    rows = clean_city_payload("Grenoble", payload)
    assert len(rows) == 1
    assert rows[0]["city"] == "Grenoble"
    assert rows[0]["pm10"] == 10.0


def test_missing_timestamp_is_dropped():
    payload = make_payload(["2026-07-01T00:00", "", "2026-07-01T02:00"])
    rows = clean_city_payload("Grenoble", payload)
    timestamps = [r["timestamp"] for r in rows]
    assert "" not in timestamps
    assert len(rows) == 2


def test_aberrant_value_becomes_none_not_dropped():
    # pm10 négatif -> hors bornes plausibles -> normalisé à None,
    # mais la ligne est gardée car pm2_5 reste valide
    payload = make_payload(["2026-07-01T00:00"], pm10=[-5.0])
    rows = clean_city_payload("Grenoble", payload)
    assert len(rows) == 1
    assert rows[0]["pm10"] is None
    assert rows[0]["pm2_5"] == 5.0


def test_row_dropped_if_all_variables_invalid():
    payload = {
        "hourly": {
            "time": ["2026-07-01T00:00"],
            "pm10": [-1],
            "pm2_5": [None],
            "carbon_monoxide": [-1],
            "nitrogen_dioxide": [None],
            "ozone": [-1],
            "european_aqi": [None],
        }
    }
    rows = clean_city_payload("Grenoble", payload)
    assert rows == []


def test_clean_all_deduplicates_and_sorts():
    entry1 = {
        "city": "Lyon",
        "raw": make_payload(["2026-07-01T02:00", "2026-07-01T00:00"]),
    }
    # ville dupliquée avec un timestamp en commun -> doit être dédupliquée
    entry2 = {
        "city": "Lyon",
        "raw": make_payload(["2026-07-01T00:00"]),
    }
    rows = clean_all([entry1, entry2])
    timestamps = [r["timestamp"] for r in rows]
    assert timestamps == sorted(timestamps)
    assert len(rows) == 2  # pas 3, malgré le doublon


def test_clean_all_multiple_cities():
    entries = [
        {"city": "Paris", "raw": make_payload(["2026-07-01T00:00"])},
        {"city": "Lille", "raw": make_payload(["2026-07-01T00:00"])},
    ]
    rows = clean_all(entries)
    cities = {r["city"] for r in rows}
    assert cities == {"Paris", "Lille"}
