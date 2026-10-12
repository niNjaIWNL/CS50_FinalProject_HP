import sqlite3
from unittest.mock import Mock

import pytest

from cs50_final_active import create_app, pages


@pytest.fixture
def search_client(tmp_path, monkeypatch):
    database = tmp_path / "instance" / "flights.sqlite3"
    database.parent.mkdir()
    with sqlite3.connect(database) as connection:
        connection.execute("""
            CREATE TABLE flights (
                airline TEXT, number TEXT, origin_airport TEXT, dest_airport TEXT,
                dep_percentage REAL, arr_percentage REAL, avg_dept REAL, avg_arr REAL
            )
        """)
        connection.executemany(
            "INSERT INTO flights VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("GLO", "0782", "SBBR", "SBGR", 12.4, 9.8, 58.2, 46.1),
                ("AZU", "9501", "SBBR", "SBGR", 20.0, 10.0, 60.0, 45.0),
                ("AZU", "9501", "SBBR", "SBCT", 30.0, 15.0, 70.0, 50.0),
                ("TAM", "0001", "SBBR", "SBGR", 0.0, 0.0, None, None),
            ],
        )
    monkeypatch.setattr(
        pages, "__file__", str(tmp_path / "src" / "cs50_final_active" / "pages.py")
    )
    lookup = Mock(side_effect=lambda code: {"name": f"Airport {code}", "city": "City"})
    monkeypatch.setattr(pages, "get_airport", lookup)
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client(), lookup


def test_home_page():
    app = create_app()
    app.config.update(TESTING=True)
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Know your flight" in response.data
    assert b'name="airline"' in response.data
    assert b'name="flight"' in response.data
    assert b'name="origin"' not in response.data
    assert b'name="destination"' not in response.data


def test_search_discovers_route_and_statistics(search_client):
    client, lookup = search_client
    response = client.post("/search", data={"airline": " glo ", "flight": " 0782 "})
    assert response.status_code == 200
    for value in (b"SBBR", b"SBGR", b"Airport SBBR", b"Airport SBGR", b"12.40", b"9.80"):
        assert value in response.data
    assert lookup.call_count == 2
    assert b'value="0782"' in response.data


def test_search_keeps_multiple_routes_separate(search_client):
    client, lookup = search_client
    response = client.post("/search", data={"airline": "AZU", "flight": "9501"})
    assert response.status_code == 200
    assert b"2 historical routes found" in response.data
    assert b"SBCT" in response.data and b"SBGR" in response.data
    assert b"20.00" in response.data and b"30.00" in response.data
    assert response.data.count(b'class="route-result"') == 2
    assert lookup.call_count == 3  # The shared origin is requested only once.
    assert b'id="departure-title-1"' in response.data
    assert b'id="departure-title-2"' in response.data


def test_search_without_match_skips_airport_requests(search_client):
    client, lookup = search_client
    response = client.post("/search", data={"airline": "XXX", "flight": "9999"})
    assert response.status_code == 200
    assert b"No historical data found" in response.data
    lookup.assert_not_called()


def test_search_missing_input(search_client):
    client, lookup = search_client
    response = client.post("/search", data={"airline": "GLO", "flight": " "})
    assert response.status_code == 400
    assert b"Enter an airline ICAO code and flight number." in response.data
    lookup.assert_not_called()


def test_search_no_delays_and_missing_airport_details(search_client):
    client, lookup = search_client
    lookup.side_effect = None
    lookup.return_value = None
    response = client.post("/search", data={"airline": "TAM", "flight": "0001"})
    assert response.status_code == 200
    assert response.data.count(b"no recorded delays") == 2
    assert response.data.count(b"Airport details unavailable.") == 2
    assert b"0.00" in response.data


def test_search_binds_input_as_sql_parameters(search_client):
    client, lookup = search_client
    response = client.post(
        "/search", data={"airline": "GLO' OR 1=1 --", "flight": "0782"}
    )
    assert response.status_code == 200
    assert b"No historical data found" in response.data
    lookup.assert_not_called()


def test_airport_lookup_without_exact_match(monkeypatch):
    monkeypatch.setenv("AIRPORTS_API", "test-key")
    response = Mock()
    response.json.return_value = [{"icao": "SBGR", "name": "Other airport"}]
    monkeypatch.setattr(pages.requests, "get", Mock(return_value=response))
    assert pages.get_airport("SBBR") is None
