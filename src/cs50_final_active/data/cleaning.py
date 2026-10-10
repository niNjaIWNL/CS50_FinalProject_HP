from pathlib import Path

import pandas as pd

TIMESTAMP_COLUMNS = [
    "Partida Prevista",
    "Partida Real",
    "Chegada Prevista",
    "Chegada Real",
]

FLIGHT_COLUMNS = [
    "ICAO Empresa Aérea",
    "Número Voo",
    "ICAO Aeródromo Origem",
    "ICAO Aeródromo Destino",
    *TIMESTAMP_COLUMNS,
]


def load_flights(path: str | Path) -> pd.DataFrame:
    """Read a VRA CSV and retain completed flights with four valid timestamps."""
    flights = pd.read_csv(
        path,
        sep=";",
        skiprows=1,
        encoding="utf-8-sig",
        usecols=[*FLIGHT_COLUMNS, "Situação Voo"],
        dtype="string",
        na_values=["null"],
    )

    status = flights["Situação Voo"].str.strip().str.upper()
    flights = flights.loc[status.eq("REALIZADO"), FLIGHT_COLUMNS].copy()

    for column in TIMESTAMP_COLUMNS:
        flights[column] = pd.to_datetime(
            flights[column].str.strip(), format="ISO8601", errors="coerce"
        )

    return flights.dropna(subset=TIMESTAMP_COLUMNS).reset_index(drop=True)
