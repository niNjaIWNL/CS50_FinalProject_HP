from cs50_final_active.data.cleaning import load_flights
from pathlib import Path
import pandas as pd


def load_and_clean_flights():
    """ This function loads and cleans each seven datasets"""
    flight_data = {p.stem: load_flights(p) for p in Path("assets").glob("*.csv")}
    return flight_data


flight_data = load_and_clean_flights()

total = pd.concat(flight_data, axis=0)


total["departure_delay_minutes"] = (
    total["Partida Real"] - total["Partida Prevista"]
).dt.total_seconds() / 60

total["arrival_delay_minutes"] = (
    total["Chegada Real"] - total["Chegada Prevista"]
).dt.total_seconds() / 60


flight_averages = []

for (airline, flight_number, origin, destination), flights in total.groupby(
    ["ICAO Empresa Aérea", "Número Voo", "ICAO Aeródromo Origem", "ICAO Aeródromo Destino"]
):
    departure_delays = []
    arrival_delays = []

    for departure, arrival in zip(
        flights["departure_delay_minutes"],
        flights["arrival_delay_minutes"],
    ):
        if departure > 30:
            departure_delays.append(departure)

        if arrival > 30:
            arrival_delays.append(arrival)

    average_departure = None
    average_arrival = None
    total_flights = len(flights)
    departure_delay_percentage = len(departure_delays) / total_flights * 100
    arrival_delay_percentage = len(arrival_delays) / total_flights * 100

    if departure_delays:
        average_departure = sum(departure_delays) / len(departure_delays)

    if arrival_delays:
        average_arrival = sum(arrival_delays) / len(arrival_delays)

    flight_averages.append({
        "airline_icao": airline,
        "flight_number": flight_number,
        "origin_icao": origin,
        "destination_icao": destination,
        "total_flights": total_flights,
        "delayed_departures": len(departure_delays),
        "delayed_arrivals": len(arrival_delays),
        "departure_delay_percentage": departure_delay_percentage,
        "arrival_delay_percentage": arrival_delay_percentage,
        "average_departure_delay_minutes": average_departure,
        "average_arrival_delay_minutes": average_arrival,
    })

flight_summary = pd.DataFrame(flight_averages)
print(flight_summary.head(10).to_string(index=False))
