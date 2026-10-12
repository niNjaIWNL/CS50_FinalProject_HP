import os
import sqlite3
from pathlib import Path

import requests
from flask import Blueprint, render_template, request

bp = Blueprint("pages", __name__)


def get_airport(icao):
    api_key = os.environ.get("AIRPORTS_API")
    if not api_key:
        return None
    try:
        response = requests.get(
            "https://api.api-ninjas.com/v1/airports",
            params={"icao": icao},
            headers={"X-Api-Key": api_key},
            timeout=10,
        )
        response.raise_for_status()
        airports = response.json()
    except (requests.RequestException, ValueError):
        return None

    return next(
        (airport for airport in airports if airport.get("icao") == icao),
        None,
    )


@bp.get("/")
def home():
    return render_template("pages/home.html", flight_info=None, results=[])


@bp.post("/search")
def search():
    flight_info = {
        "airline": request.form.get("airline", "").strip().upper(),
        "flight": request.form.get("flight", "").strip().upper(),
    }

    if not all(flight_info.values()):
        return render_template(
            "pages/home.html", flight_info=flight_info, results=[],
            error="Enter an airline ICAO code and flight number.",
        ), 400

    flights_db = Path(__file__).resolve().parents[2] / "instance" / "flights.sqlite3"
    with sqlite3.connect(flights_db.as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        db = connection.cursor()

        flights = db.execute(
            """
            SELECT origin_airport, dest_airport,
                   dep_percentage, arr_percentage, avg_dept, avg_arr
            FROM flights
            WHERE airline = ?
            AND number = ?
            ORDER BY origin_airport, dest_airport
            """,
            (
                flight_info["airline"],
                flight_info["flight"],
            ),
        ).fetchall()

    results = []
    airports = {}
    for flight in flights:
        origin = flight["origin_airport"]
        destination = flight["dest_airport"]
        for code in (origin, destination):
            if code not in airports:
                airports[code] = get_airport(code)
        results.append({
            "origin": origin,
            "destination": destination,
            "flight": flight,
            "origin_airport": airports[origin],
            "destination_airport": airports[destination],
        })

    return render_template(
        "pages/home.html", flight_info=flight_info, results=results,
    )
