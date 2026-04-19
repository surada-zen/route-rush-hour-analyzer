from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """Render the homepage with the input form."""
    return render_template("index.html")


@app.route("/result", methods=["GET", "POST"])
def result():
    """Render result page with mock analysis data.

    Future integration:
    - Replace mock values with route/travel-time analysis
    - Connect to external mapping APIs
    - Persist user searches in a database
    """
    # Pull values from form submission (POST) and allow query params (GET).
    origin = request.form.get("origin") or request.args.get("origin") or "Not provided"
    destination = request.form.get("destination") or request.args.get("destination") or "Not provided"
    departure_time = (
        request.form.get("departure_time")
        or request.args.get("departure_time")
        or "Not provided"
    )
    travel_mode = request.form.get("travel_mode") or request.args.get("travel_mode") or "drive"

    # Mock placeholder data for now.
    # Future integration: compute these from live traffic + historical trends.
    mock_data = {
        "recommended_time": "15 minutes earlier",
        "time_saved": "8 minutes",
        "explanation": "Traffic is usually heavier near your selected departure window.",
    }

    return render_template(
        "result.html",
        origin=origin,
        destination=destination,
        departure_time=departure_time,
        travel_mode=travel_mode,
        recommended_time=mock_data["recommended_time"],
        time_saved=mock_data["time_saved"],
        explanation=mock_data["explanation"],
    )


if __name__ == "__main__":
    # Future integration: move host/port/debug settings to environment variables.
    app.run(debug=True)
