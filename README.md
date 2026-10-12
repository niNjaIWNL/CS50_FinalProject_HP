# HoldingPattern
#### Video Demo: <URL HERE>
#### Description:

HoldingPattern is a flight history web application developed as a CS50 final project. It helps travelers answer a practical question before flying: how often has this flight been delayed, and how long were those delays? Users enter an airline ICAO code and flight number. The application retrieves the origin and destination from SQLite and displays historical departure and arrival statistics alongside airport names and cities. If a flight number has multiple historical routes, each route is displayed separately.

The goal is to turn flight records into understandable information. Departure and arrival are analyzed separately because a flight can leave late and recover time before landing. HoldingPattern presents historical performance, rather than live tracking or a guaranteed prediction of the next flight. Its dataset covers January through July 2026.

## Architecture and system design

The system has two distinct workflows: 
>***Data Analysis***: preparing the historical data and serving user searches. Data preparation runs offline, using Pandas to clean seven monthly CSV files, calculate delays, and aggregate statistics. Those summaries are inserted into a local SQLite database. During normal operation, Flask reads the prepared summaries without repeating the analysis or loading the CSV files.

>***Full-Stack Development***: building the web application with a server-rendered design. The web application follows a server-rendered design. A browser submits an HTML form to Flask, which queries SQLite and requests airport details from API Ninjas with REST API calls. Jinja combines the results with the page template and returns HTML to the browser. The API key remains in the backend UV environment.

SQLite suits the project's local deployment and fixed historical dataset: it stores the summaries in one file without requiring a separate database server. Precomputing both percentages and averages makes searches simple. A composite primary key identifies each combination of airline, flight number, origin, and destination, preventing duplicate summaries.

## Technologies and project structure

The project uses Python for backend development, Flask for HTTP requests routing, Jinja2 for HTML rendering, Python/pandas for data processing, Python's built-in `sqlite3` module for database management and query, and Requests for external REST APIs HTTP calls. UV manages dependencies and the virtual environment, while `uv.lock` records resolved package versions. Pytest supports automated checks, and Ruff is available for linting. Waitress is included as a WSGI deploymentserver dependency.

The main files and directories are:

- `src/cs50_final_active/__init__.py`: defines the Flask application factory and registers the pages blueprint.
- `src/cs50_final_active/pages.py`: handles the homepage, submitted searches, database lookups, and airport API requests.
- `src/cs50_final_active/data/cleaning.py`: provides the reusable CSV cleaning function.
- `src/cs50_final_active/data/analysis.py`: combines datasets, calculates summaries, and inserts them into SQLite.
- `src/cs50_final_active/templates/pages/home.html`: renders the search form, airport details, and result cards.
- `src/cs50_final_active/static/`: contains the CSS and cloud background image.
- `assets/`: holds the seven source CSV files.
- `instance/flights.sqlite3`: stores the prepared flight summaries.
- `tests/`: contains cleaning, database, route-analysis, homepage, and API-related checks.

## Data cleaning and calculations

The cleaner reads semicolon-separated CSVs, skips the initial update notice, and handles UTF-8 encoding. It keeps only records marked `REALIZADO`, excluding cancelled or uncompleted flights. Scheduled and actual departure and arrival values are converted to datetime objects. Records missing any valid timestamp are discarded. Flight numbers remain strings to preserve leading zeros.

For each retained flight, departure delay is actual departure minus scheduled departure; arrival delay uses the corresponding arrival timestamps. Durations are converted to total minutes. For simplicity, a flight is classified as delayed only when the difference exceeds 30 minutes. Exactly 30 minutes does not qualify.

Records are grouped by airline ICAO, flight number, origin, and destination. Each summary contains total flights, delayed departure and arrival counts, their percentages, and average delay durations. Percentages equal delayed flights divided by total retained flights, multiplied by 100. Duration averages include only qualifying delays and use their full duration: a 45-minute delay contributes 45 minutes. Missing averages become SQL `NULL` when no flights qualify.

## Search experience

`GET /` displays the homepage. `POST /search` trims and uppercases submitted values, then performs a parameterized query for the airline and flight number. Routes and their statistics come from the database. API Ninjas' `/v1/airports` endpoint supplies airport names and cities through ICAO lookups authenticated with an `X-Api-Key` header. Repeated airport codes within a search are looked up only once.

The responsive frontend uses navy typography, blue accents, a cloud hero, and a floating search form. Separate departure and arrival cards display percentages and average minutes. Missing summaries produce a clear message, and missing airport details have a fallback. Historical coverage and the delay threshold are explained on the page.

## Local running and verification

From the project root, install dependencies and start Flask:

```powershell
uv sync
$env:AIRPORTS_API = "your-api-ninjas-key"
uv run flask --app cs50_final_active run --debug
```

The application requires the prepared SQLite database. Its `flights` table must exist before the one-time analysis script runs. That script inserts records on execution; rerunning it against populated data can cause primary-key conflicts. The ignored `instance/` directory and API key must be configured separately on another machine.

Database tests compare stored percentages with counts and reconstruct counts from cleaned CSVs. Run those read-only checks with `uv run pytest tests/test_database.py -v`. Results describe completed flights with valid timestamps; cancellations and excluded records are outside the reported percentages.

## Sources for this project:

- ANAC Datasets: https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Voo%20Regular%20Ativo%20%28VRA%29/2026/
- Uv environment: https://uv.run/
- Uv flask setup: https://pydevtools.com/handbook/tutorial/set-up-a-flask-project-with-uv/
- Pytest: https://docs.pytest.org/en/stable/
- Airport API Ninjas: https://api-ninjas.com/api/airports
- W3Schools: https://www.w3schools.com/
- Python documentation: https://docs.python.org/3/
- FreeCodeCamp SQLite with Python: https://www.freecodecamp.org/news/work-with-sqlite-in-python-handbook/
