from flask import Blueprint, render_template, request
import sqlite3
from pathlib import Path

bp = Blueprint("pages", __name__)


@bp.get("/")
def home():
    return render_template("pages/home.html", flight_info=None)

@bp.post("/search")
def search():
    flight_info = {
        "airline": request.form.get("airline", "").strip(),
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

    return render_template("pages/home.html", flight_info=flight_info, flight=flight)