import os
import requests

response = requests.get(
    "https://api.api-ninjas.com/v1/airports",
    params={"icao": "SBBR"},
    headers={"X-Api-Key": os.environ["AIRPORTS_API"]},
    timeout=10,
)

response.raise_for_status()
airports = response.json()

airport = next(
    (item for item in airports if item["icao"] == "SBBR"),
    None,
)

if airport is not None:
    print("ICAO:", airport["icao"])
    print("Name:", airport["name"])
    print("City:", airport["city"])
else:
    print("No exact airport match found.")