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
    origin_name = request.form.get("origin_name", "")
    destination_name = request.form.get("destination_name", "")

    # Read map-selected coordinates from hidden form fields.
    origin_lat = request.form.get("origin_lat", "")
    origin_lng = request.form.get("origin_lng", "")
    destination_lat = request.form.get("destination_lat", "")
    destination_lng = request.form.get("destination_lng", "")
    route_distance_km = request.form.get("route_distance_km", "")
    route_duration_min = request.form.get("route_duration_min", "")

    departure_time = request.form.get("departure_time", "")
    travel_mode = request.form.get("travel_mode", "")

    selected_dt = datetime.fromisoformat(departure_time)

    # Build nearby departure slots around the selected time.
    # The selected slot baseline can now come from real OSRM route duration,
    # while nearby-slot adjustments are still heuristic (not traffic-aware yet).
    # A future step will replace this with real time-dependent traffic API data.
    slot_offsets = [-60, -30, 0, 30, 60]
    slot_datetimes = [selected_dt + timedelta(minutes=offset) for offset in slot_offsets]

    # Prefer real baseline duration from OSRM route response if present.
    # If missing/invalid, fall back to previous mock baseline-by-mode behavior.
    try:
        real_baseline_duration = float(route_duration_min)
        has_real_baseline = real_baseline_duration > 0
    except (TypeError, ValueError):
        real_baseline_duration = 0.0
        has_real_baseline = False

    mode_base_duration = {"drive": 42, "bike": 56, "walk": 74}
    mock_base_duration = mode_base_duration.get(travel_mode, 42)

    selected_hour = selected_dt.hour
    if has_real_baseline:
        baseline_duration = real_baseline_duration
        if 6 <= selected_hour < 9 or 15 <= selected_hour < 18:
            # Rush-like periods: earlier departures often slightly better.
            percent_deltas = {-60: -0.10, -30: -0.05, 0: 0.0, 30: 0.07, 60: 0.12}
        elif 9 <= selected_hour < 11 or 18 <= selected_hour < 20:
            # Congestion easing: some later departures can improve.
            percent_deltas = {-60: 0.08, -30: 0.04, 0: 0.0, 30: -0.04, 60: -0.08}
        else:
            # Off-peak: smaller differences around baseline.
            percent_deltas = {-60: 0.03, -30: -0.01, 0: 0.0, 30: 0.02, 60: 0.04}

        duration_deltas = {
            offset: round(baseline_duration * percent_deltas[offset]) for offset in slot_offsets
        }
    else:
        baseline_duration = mock_base_duration
        if 6 <= selected_hour < 9 or 15 <= selected_hour < 18:
            duration_deltas = {-60: -8, -30: -4, 0: 0, 30: 5, 60: 9}
        elif 9 <= selected_hour < 11 or 18 <= selected_hour < 20:
            duration_deltas = {-60: 7, -30: 3, 0: 0, 30: -3, 60: -6}
        else:
            duration_deltas = {-60: 2, -30: -1, 0: 0, 30: 1, 60: 3}

    compared_slots = []
    for offset, slot_dt in zip(slot_offsets, slot_datetimes):
        duration = max(1, round(baseline_duration + duration_deltas[offset]))
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
    best_offset = best_slot["offset"]

    for slot in compared_slots:
        slot["is_selected"] = slot["offset"] == 0
        slot["is_best"] = slot["time"] == best_departure_time

    # Heuristic messaging based on nearby-slot comparison.
    # This is not traffic-aware yet; a future step will use real time-dependent traffic APIs.
    if time_saved > 0:
        if best_offset < 0:
            timing_hint = "leaving a bit earlier"
            traffic_insight = "A slightly earlier departure appears more efficient for this route."
        elif best_offset > 0:
            timing_hint = "leaving a bit later"
            traffic_insight = "A slightly later departure appears more efficient for this route."
        else:
            timing_hint = "staying with your selected time"
            traffic_insight = "Nearby time slots show only minor variation for this route."

        explanation = (
            f"You selected {_format_slot_time(selected_dt)}, with an estimated "
            f"{selected_time_duration} minute trip. "
            f"The recommended departure is {best_departure_time}, with an estimated "
            f"{best_time_duration} minutes. Based on nearby-slot comparison, "
            f"{timing_hint} can reduce expected travel time by about {time_saved} minutes."
        )
    else:
        explanation = (
            f"You selected {_format_slot_time(selected_dt)}, and nearby options are all about "
            f"{best_time_duration} minutes. Your selected time is already one of the best nearby choices."
        )
        traffic_insight = (
            "Nearby time slots show only minor variation, so your selected time is already reasonable."
        )

    return render_template(
        "result.html",
        origin_name=origin_name,
        destination_name=destination_name,
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        destination_lat=destination_lat,
        destination_lng=destination_lng,
        route_distance_km=route_distance_km,
        route_duration_min=route_duration_min,
        departure_time=_format_slot_time(selected_dt),
        travel_mode=travel_mode,
        compared_slots=compared_slots,
        best_departure_time=best_departure_time,
        best_time_duration=best_time_duration,
        selected_time_duration=selected_time_duration,
        time_saved=time_saved,
        explanation=explanation,
        traffic_insight=traffic_insight,
    )


if __name__ == "__main__":
    app.run(debug=True)
