(() => {
  const form = document.getElementById("flight-form");
  const result = document.getElementById("result");
  const error = document.getElementById("error");

  const field = id => document.getElementById(id);

  // Airport names for this demonstration.
  const airports = {
    JFK: "John F. Kennedy · New York",
    LHR: "Heathrow · London",
    GRU: "Guarulhos · São Paulo",
    LIS: "Humberto Delgado · Lisbon",
    LAX: "Los Angeles International"
  };

  // These are illustrative examples, not verified flight records.
  const examples = [
    {
      airline: "British Airways",
      flight: "BA 178",
      origin: "JFK",
      destination: "LHR",
      aircraft: "Boeing 777 (sample)"
    },
    {
      airline: "TAP Air Portugal",
      flight: "TP 88",
      origin: "GRU",
      destination: "LIS",
      aircraft: "Airbus A330 (sample)"
    },
    {
      airline: "American Airlines",
      flight: "AA 10",
      origin: "LAX",
      destination: "JFK",
      aircraft: "Airbus A321 (sample)"
    }
  ];

  function setText(id, value) {
    // Render user input as text rather than HTML.
    field(id).textContent = value;
  }

  function normalizeFlight(value) {
    return value.replace(/\s+/g, "").toUpperCase();
  }

  function showError(message) {
    error.textContent = message;
    error.hidden = false;
    result.hidden = true;
  }

  form.addEventListener("submit", event => {
    event.preventDefault();

    const input = {
      airline: field("airline").value.trim(),
      flight: field("flight").value.trim().toUpperCase(),
      origin: field("origin").value.trim().toUpperCase(),
      destination: field("destination").value.trim().toUpperCase()
    };

    if (!input.airline || !input.flight) {
      showError("Enter an airline and flight number.");
      return;
    }

    if (input.origin === input.destination) {
      showError("Choose different origin and destination airports.");
      return;
    }

    error.hidden = true;

    // Replace this lookup with a request to your backend flight API.
    const sample = examples.find(example =>
      example.airline.toLowerCase() === input.airline.toLowerCase() &&
      normalizeFlight(example.flight) === normalizeFlight(input.flight) &&
      example.origin === input.origin &&
      example.destination === input.destination
    );

    setText("result-title", `${input.airline} · ${input.flight}`);
    setText("from-code", input.origin);
    setText("to-code", input.destination);

    setText(
      "from-name",
      airports[input.origin] ?? "Airport details unavailable"
    );

    setText(
      "to-name",
      airports[input.destination] ?? "Airport details unavailable"
    );

    setText("flight-detail", input.flight);
    setText("aircraft-detail", sample?.aircraft ?? "Not available");

    setText(
      "result-note",
      sample
        ? "Illustrative aircraft data only. Schedules, gates, and live status require a flight data service."
        : "Your entered route is shown above. This demo cannot verify that the flight exists or serves this route."
    );

    result.hidden = false;

    const reducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    result.scrollIntoView({
      behavior: reducedMotion ? "auto" : "smooth",
      block: "center"
    });
  });

  document.querySelectorAll("[data-example]").forEach(button => {
    button.addEventListener("click", () => {
      const example = examples[Number(button.dataset.example)];

      for (const key of ["airline", "flight", "origin", "destination"]) {
        field(key).value = example[key];
      }

      form.requestSubmit();
    });
  });

  document.querySelectorAll(".airport-input").forEach(input => {
    input.addEventListener("input", () => {
      input.value = input.value.toUpperCase();
    });
  });
})();