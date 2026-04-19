from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result", methods=["POST"])
def result():
    # Read values submitted by the user from the form.
    origin = request.form.get("origin", "")
    destination = request.form.get("destination", "")
    departure_time = request.form.get("departure_time", "")
    travel_mode = request.form.get("travel_mode", "")

    # TODO: Replace mock outputs with real route analysis logic.
    # Future integration point for traffic data + route recommendation engine.
    recommended_time = "15 minutes earlier"
    time_saved = "~12 minutes"
    explanation = "Mock recommendation: leaving a bit earlier avoids peak congestion."

    return render_template(
        "result.html",
        origin=origin,
        destination=destination,
        departure_time=departure_time,
        travel_mode=travel_mode,
        recommended_time=recommended_time,
        time_saved=time_saved,
        explanation=explanation,
    )


if __name__ == "__main__":
    app.run(debug=True)
