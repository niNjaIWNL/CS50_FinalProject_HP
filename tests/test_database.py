import sqlite3
from pathlib import Path

import pytest
import pandas as pd
from typing import cast

from cs50_final_active.data.cleaning import load_flights

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def read_database():
    path = PROJECT_ROOT / "instance" / "flights.sqlite3"

    # Read-only mode to prevent changes or accidental database change
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute("SELECT * FROM flights").fetchall()

def test_stored_percentages():
    rows = read_database()
    assert rows, "The database is empty"

    for row in rows:
        identifier = (
            row["airline"],
            row["number"],
            row["origin_airport"],
            row["dest_airport"],
        )

        total = row["total_flights"]
        assert total > 0, identifier

        for count_column, percentage_column in [
            ("delayed_dep", "dep_percentage"),
            ("delayed_arr", "arr_percentage"),
        ]:
            count = row[count_column]
            percentage = row[percentage_column]

            assert 0 <= count <= total, identifier
            assert percentage is not None, identifier
            assert 0 <= percentage <= 100, identifier
            assert percentage == pytest.approx(
                count / total * 100
            ), identifier

def test_database_counts_match_csvs():
    paths = sorted((PROJECT_ROOT / "assets").glob("*.csv"))
    assert len(paths) == 7

    flights = pd.concat(
        [load_flights(path) for path in paths],
        ignore_index=True,
    )

    flights["departure_delayed"] = (
        flights["Partida Real"] - flights["Partida Prevista"]
    ).dt.total_seconds() > 30 * 60

    flights["arrival_delayed"] = (
        flights["Chegada Real"] - flights["Chegada Prevista"]
    ).dt.total_seconds() > 30 * 60

    expected = flights.groupby([
        "ICAO Empresa Aérea",
        "Número Voo",
        "ICAO Aeródromo Origem",
        "ICAO Aeródromo Destino",
    ]).agg(
        total_flights=("Número Voo", "size"),
        delayed_dep=("departure_delayed", "sum"),
        delayed_arr=("arrival_delayed", "sum"),
    )

    stored = {
        (
            row["airline"],
            row["number"],
            row["origin_airport"],
            row["dest_airport"],
        ): row
        for row in read_database()
    }

    assert set(stored) == set(expected.index)

    for index, counts in expected.iterrows():
        identifier = cast(tuple[str, str, str, str], index)

        for column in ["total_flights", "delayed_dep", "delayed_arr"]:
            assert stored[identifier][column] == counts[column], identifier