from flask import Blueprint, render_template, request
import sqlite3
from pathlib import Path
import os
import requests

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
        (airport for airport in airports if airport.get("icao")== icao),
    )


@bp.get("/")
def home():
    return render_template("pages/home.html", flight_info=None)

@bp.post("/search")
def search():
    flight_info = {
        "airline": request.form.get("airline", "").strip().upper(),
        "flight": request.form.get("flight", "").strip().upper(),
        "origin": request.form.get("origin", "").strip().upper(),
        "destination": request.form.get("destination", "").strip().upper(),
    }

    """Write SQL queries to check against user input below"""
    flights_db = Path("instance/flights.sqlite3")
    with sqlite3.connect(flights_db) as connection:
        connection.row_factory = sqlite3.Row
        db = connection.cursor()

        flight = db.execute(
            """
            SELECT dep_percentage, arr_percentage, avg_dept, avg_arr
            FROM flights
            WHERE airline = ?
            AND number = ?
            AND origin_airport = ?
            AND dest_airport = ?
            """,
            (
                flight_info["airline"],
                flight_info["flight"],
                flight_info["origin"],
                flight_info["destination"],
            ),
        ).fetchone()

    origin_airport = get_airport(flight_info["origin"])
    destination_airport = get_airport(flight_info["destination"])

    return render_template("pages/home.html", flight_info=flight_info, flight=flight, origin_airport=origin_airport, destination_airport=destination_airport)