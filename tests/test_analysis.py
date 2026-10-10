import runpy
from pathlib import Path

import pytest


def test_sbbr_sbgr_departure_statistics(monkeypatch, capsys):
    """Check route totals and weighted delay statistics against individual flights."""
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    analysis = runpy.run_module("cs50_final_active.data.analysis")
    capsys.readouterr()

    flights = analysis["total"]
    route = flights.loc[
        flights["ICAO Aeródromo Origem"].eq("SBBR")
        & flights["ICAO Aeródromo Destino"].eq("SBGR")
    ]
    assert not route.empty

    departure_minutes = (
        route["Partida Real"] - route["Partida Prevista"]
    ).dt.total_seconds() / 60
    delayed = departure_minutes.loc[departure_minutes.gt(30)]
    assert not delayed.empty

    summary = analysis["flight_summary"]
    route_summary = summary.loc[
        summary["origin_icao"].eq("SBBR")
        & summary["destination_icao"].eq("SBGR")
    ]
    total_flights = route_summary["total_flights"].sum()
    delayed_departures = route_summary["delayed_departures"].sum()
    percentage = delayed_departures / total_flights * 100
    average_delay = (
        route_summary["average_departure_delay_minutes"].fillna(0)
        * route_summary["delayed_departures"]
    ).sum() / delayed_departures

    assert total_flights == len(route)
    assert delayed_departures == len(delayed)
    assert percentage == pytest.approx(len(delayed) / len(route) * 100)
    assert average_delay == pytest.approx(delayed.mean())

    print(
        f"SBBR -> SBGR: {delayed_departures}/{total_flights} departures delayed "
        f"({percentage:.2f}%), averaging {average_delay:.2f} minutes when delayed."
    )
