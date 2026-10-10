import csv

import pandas as pd
import pytest

from cs50_final_active.data.cleaning import (
    FLIGHT_COLUMNS,
    TIMESTAMP_COLUMNS,
    load_flights,
)


def test_load_flights_filters_and_preserves_identifiers(tmp_path):
    valid = [
        "LAN", "0782", "SBCT", "SCEL",
        "2026-01-13 17:40:00", "2026-01-13 17:45:00.100000000",
        "2026-01-13 21:26:00", "2026-01-13 21:28:00", "REALIZADO",
    ]
    cancelled = [*valid[:-1], "CANCELADO"]
    not_flown = [*valid[:-1], "NAO REALIZADO"]
    incomplete_rows = []
    for index in range(4, 8):
        for missing_value in ("null", "", "N/A", "invalid date"):
            row = valid.copy()
            row[index] = missing_value
            incomplete_rows.append(row)

    path = tmp_path / "flights.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        file.write("Atualizado em: 2026-10-07\n")
        writer = csv.writer(file, delimiter=";")
        writer.writerow([*FLIGHT_COLUMNS, "Situação Voo", "Código Justificativa"])
        for row in [valid, cancelled, not_flown, *incomplete_rows]:
            writer.writerow([*row, "N/A"])

    flights = load_flights(path)

    assert list(flights.columns) == FLIGHT_COLUMNS
    assert len(flights) == 1
    assert flights.loc[0, "Número Voo"] == "0782"
    for column in TIMESTAMP_COLUMNS:
        assert pd.api.types.is_datetime64_any_dtype(flights[column])
    departure_delay = (
        flights.loc[0, "Partida Real"] - flights.loc[0, "Partida Prevista"]
    ).total_seconds() / 60
    assert departure_delay == pytest.approx(5 + 0.1 / 60)
