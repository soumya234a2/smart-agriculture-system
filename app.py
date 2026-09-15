"""
Smart Agriculture System — Flask backend.

Routes:
    GET  /                        Dashboard UI
    GET  /api/sensor              Latest simulated IoT soil-sensor reading
    GET  /api/weather             Current weather (live API or offline fallback)
    POST /api/predict-disease     Crop leaf disease classification
    POST /api/recommend-fertilizer Fertilizer type + dosage recommendation
    GET  /api/health-trend        Synthetic 7-day crop health trend for the chart
"""
import random
from flask import Flask, jsonify, request, render_template

from model.disease_model import predict_disease
from services.fertilizer_recommender import recommend_fertilizer
from services.weather_service import get_weather, get_sensor_reading

app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/sensor")
def api_sensor():
    return jsonify(get_sensor_reading())


@app.route("/api/weather")
def api_weather():
    return jsonify(get_weather())


@app.route("/api/health-trend")
def api_health_trend():
    random.seed(7)
    trend = [round(random.uniform(65, 95), 1) for _ in range(7)]
    return jsonify({
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "health_index": trend,
    })


@app.route("/api/predict-disease", methods=["POST"])
def api_predict_disease():
    payload = request.get_json(force=True, silent=True) or {}
    required = ["mean_r", "mean_g", "mean_b", "texture_var", "lesion_ratio", "edge_density"]
    missing = [f for f in required if f not in payload]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    result = predict_disease(*(payload[f] for f in required))
    return jsonify(result)


@app.route("/api/recommend-fertilizer", methods=["POST"])
def api_recommend_fertilizer():
    payload = request.get_json(force=True, silent=True) or {}
    try:
        n, p, k = float(payload["n"]), float(payload["p"]), float(payload["k"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Provide numeric n, p, k in the request body."}), 400
    crop = payload.get("crop", "default")
    return jsonify(recommend_fertilizer(n, p, k, crop))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
