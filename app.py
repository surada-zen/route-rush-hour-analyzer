from datetime import datetime, timedelta

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def _format_slot_time(slot_dt: datetime) -> str:
    """Format date/time in a friendly way for the results page."""
    return slot_dt.strftime("%Y-%m-%d %H:%M")


@app.route("/result", methods=["POST"])
def result():
    # Read values submitted by the user from the form.
    origin = request.form.get("origin", "")
    destination = request.form.get("destination", "")
    departure_time = request.form.get("departure_time", "")
    travel_mode = request.form.get("travel_mode", "")

    selected_dt = datetime.fromisoformat(departure_time)

    # Build nearby departure slots around the selected time.
    # This will later be replaced with Google Maps API travel-time data.
    slot_offsets = [-60, -30, 0, 30, 60]
    slot_datetimes = [selected_dt + timedelta(minutes=offset) for offset in slot_offsets]

    # Simple deterministic mock duration model (minutes).
    # This mock logic will later be replaced by Google Maps API duration estimates.
    mode_base_duration = {
        "drive": 42,
        "bike": 56,
        "walk": 74,
    }
    base_duration = mode_base_duration.get(travel_mode, 42)

    selected_hour = selected_dt.hour
    if 6 <= selected_hour < 9 or 15 <= selected_hour < 18:
        # Rush hour is building: earlier departures tend to be faster.
        duration_deltas = {-60: -8, -30: -4, 0: 0, 30: 5, 60: 9}
    elif 9 <= selected_hour < 11 or 18 <= selected_hour < 20:
        # Rush hour is easing: slightly later departures can be faster.
        duration_deltas = {-60: 7, -30: 3, 0: 0, 30: -3, 60: -6}
    else:
        # Off-peak: small differences around the selected time.
        duration_deltas = {-60: 2, -30: -1, 0: 0, 30: 1, 60: 3}

    compared_slots = []
    for offset, slot_dt in zip(slot_offsets, slot_datetimes):
        duration = base_duration + duration_deltas[offset]
        compared_slots.append(
            {
                "offset": offset,
                "time": _format_slot_time(slot_dt),
                "duration": duration,
            }
        )

    best_slot = min(compared_slots, key=lambda slot: slot["duration"])
    selected_slot = next(slot for slot in compared_slots if slot["offset"] == 0)

    selected_time_duration = selected_slot["duration"]
    best_time_duration = best_slot["duration"]
    best_departure_time = best_slot["time"]
    time_saved = selected_time_duration - best_time_duration

    for slot in compared_slots:
        slot["is_selected"] = slot["offset"] == 0
        slot["is_best"] = slot["time"] == best_departure_time

    explanation = (
        "This recommendation uses simple mock travel-time estimates. "
        "A later update will replace this with live Google Maps API traffic data."
    )

    return render_template(
        "result.html",
        origin=origin,
        destination=destination,
        departure_time=_format_slot_time(selected_dt),
        travel_mode=travel_mode,
        compared_slots=compared_slots,
        best_departure_time=best_departure_time,
        best_time_duration=best_time_duration,
        selected_time_duration=selected_time_duration,
        time_saved=time_saved,
        explanation=explanation,
    )


if __name__ == "__main__":
    app.run(debug=True)
