"""
Loads the trained crop-leaf-disease RandomForest model and exposes a
simple predict() function used by the Flask API.
"""
import os
import joblib
import numpy as np
import pandas as pd

FEATURE_NAMES = ["mean_r", "mean_g", "mean_b", "texture_var", "lesion_ratio", "edge_density"]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_disease_model.pkl")

_bundle = None


def _load():
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run `python model/train_synthetic.py` first."
            )
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def predict_disease(mean_r, mean_g, mean_b, texture_var, lesion_ratio, edge_density):
    """
    Predicts the crop leaf disease category from leaf-image summary
    features and returns the label plus per-class confidence.

    In a real deployment these six features are extracted from an
    uploaded leaf photo (mean colour channels via OpenCV, texture
    variance via a Laplacian filter, lesion area ratio via colour
    thresholding, edge density via Canny edge detection).
    """
    bundle = _load()
    clf, classes = bundle["model"], bundle["classes"]
    features = pd.DataFrame(
        [[mean_r, mean_g, mean_b, texture_var, lesion_ratio, edge_density]],
        columns=FEATURE_NAMES,
    )
    proba = clf.predict_proba(features)[0]
    label = clf.classes_[int(np.argmax(proba))]
    confidence = float(np.max(proba))
    ranked = sorted(zip(clf.classes_, proba), key=lambda x: x[1], reverse=True)[:3]
    return {
        "label": label,
        "confidence": round(confidence, 3),
        "top_3": [{"label": l, "confidence": round(float(p), 3)} for l, p in ranked],
    }
