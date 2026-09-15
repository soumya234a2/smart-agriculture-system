# 🌾 Smart Agriculture System (AI & IoT-based)

An AI and IoT-based system that monitors crop and soil conditions in real
time, detects crop leaf diseases from image features, and recommends the
right fertilizer type and dosage — built as a final-year engineering
project on sustainable smart farming, awarded **"Best Innovative
Project"** at the college tech fest.

## What it does

- **Real-time monitoring** — simulates a soil-moisture + NPK IoT sensor
  node and a live weather feed, surfaced on a mobile-friendly dashboard.
- **Crop leaf disease detection** — a Random Forest classifier trained
  on leaf-image summary features (colour, texture, lesion area, edge
  density) that identifies **11 disease categories** with **~86% held-out
  accuracy**.
- **Fertilizer recommendation engine** — compares current soil N, P, K
  levels against crop-specific targets and recommends the fertilizer
  type and dosage (kg/ha) needed to close the gap.
- **Interactive dashboard** — visualizes live sensor readings, a 7-day
  crop health trend, and disease alerts in a simple UI designed for
  users with low technical literacy.
- **Deployed as a Flask web app** — accessible from both desktop and
  mobile for remote, real-time field monitoring.

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python, Flask |
| ML | scikit-learn (RandomForestClassifier), pandas, numpy |
| Frontend | HTML, CSS, Chart.js |
| Weather | OpenWeatherMap API (with an offline-safe synthetic fallback) |

## Project structure

```
smart-agriculture-system/
├── app.py                        # Flask app & API routes
├── model/
│   ├── train_synthetic.py        # Trains the disease-detection model
│   ├── disease_model.py          # Loads model, exposes predict_disease()
│   └── crop_disease_model.pkl    # Trained model (generated)
├── services/
│   ├── fertilizer_recommender.py # NPK-gap-based fertilizer logic
│   └── weather_service.py        # Weather API + IoT sensor simulation
├── templates/index.html          # Dashboard UI
├── static/css/style.css
├── static/js/dashboard.js
└── requirements.txt
```

## How the disease model works

Real deployments would extract features from an uploaded leaf photo via
OpenCV (mean RGB channels, a Laplacian-based texture variance, a
colour-threshold lesion-area ratio, and Canny edge density). Since this
repo focuses on the full pipeline rather than an image dataset,
`train_synthetic.py` generates a labelled synthetic dataset with
realistic per-class feature overlap and trains a `RandomForestClassifier`
on it end-to-end — data generation → train/test split → evaluation →
serialized model — so `disease_model.py` and the `/api/predict-disease`
route work exactly as they would against real extracted features.

## Getting started

```bash
git clone https://github.com/soumya234a2/smart-agriculture-system.git
cd smart-agriculture-system
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Train the disease-detection model (writes model/crop_disease_model.pkl)
python model/train_synthetic.py

# Run the app
python app.py
```

Open **http://localhost:5000** in your browser.

Optional — for live weather instead of the synthetic fallback, set an
[OpenWeatherMap](https://openweathermap.org/api) API key:

```bash
export OPENWEATHER_API_KEY=your_key_here
```

## API reference

| Method | Route | Description |
|---|---|---|
| GET | `/api/sensor` | Latest simulated soil-sensor reading |
| GET | `/api/weather` | Current weather for the field location |
| GET | `/api/health-trend` | 7-day crop health index for the chart |
| POST | `/api/predict-disease` | Leaf disease prediction from 6 image features |
| POST | `/api/recommend-fertilizer` | Fertilizer type + dosage from NPK + crop |

## Author

**Soumyaranjan Naik** — B.Tech Computer Science Engineering
[GitHub](https://github.com/soumya234a2) · [LinkedIn](https://linkedin.com/in/Soumyaranjan-Naik)
