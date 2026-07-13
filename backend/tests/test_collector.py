from unittest.mock import MagicMock, patch

import pytest
import requests

from app.collector import CollectorError, collect_all_cities, fetch_city_air_quality


def _mock_response(json_body, status_ok=True):
    resp = MagicMock()
    resp.json.return_value = json_body
    if status_ok:
        resp.raise_for_status.return_value = None
    else:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
    return resp


@patch("app.collector.requests.get")
def test_fetch_city_air_quality_success(mock_get):
    mock_get.return_value = _mock_response({"hourly": {"time": ["2026-07-01T00:00"], "pm10": [5.0]}})
    data = fetch_city_air_quality(45.18, 5.72)
    assert "hourly" in data
    mock_get.assert_called_once()


@patch("app.collector.requests.get")
def test_fetch_city_air_quality_network_error_raises_collector_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("no network")
    with pytest.raises(CollectorError):
        fetch_city_air_quality(45.18, 5.72)


@patch("app.collector.requests.get")
def test_fetch_city_air_quality_missing_hourly_field_raises(mock_get):
    mock_get.return_value = _mock_response({"unexpected": "shape"})
    with pytest.raises(CollectorError):
        fetch_city_air_quality(45.18, 5.72)


@patch("app.collector.requests.get")
def test_collect_all_cities_skips_failing_city(mock_get):
    ok_response = _mock_response({"hourly": {"time": ["2026-07-01T00:00"], "pm10": [5.0]}})

    def side_effect(*args, **kwargs):
        if kwargs["params"]["latitude"] == 999:
            raise requests.exceptions.Timeout("timeout")
        return ok_response

    mock_get.side_effect = side_effect
    cities = [
        {"name": "VilleOK", "lat": 45.0, "lon": 5.0},
        {"name": "VilleKO", "lat": 999, "lon": 5.0},
    ]
    results = collect_all_cities(cities)
    assert len(results) == 1
    assert results[0]["city"] == "VilleOK"
