"""
Trains a RandomForest classifier that detects crop leaf disease categories
from simple leaf-image summary features (mean RGB, texture variance,
lesion-area ratio, edge density).

In production these features would come from real leaf photographs
(via OpenCV pre-processing). Here we generate a labelled synthetic
dataset with realistic per-class feature distributions so the full
pipeline -- data -> features -> model -> evaluation -- can be run and
inspected end to end.

Run:
    python model/train_synthetic.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

DISEASE_CLASSES = [
    "Healthy",
    "Leaf_Blight",
    "Powdery_Mildew",
    "Bacterial_Spot",
    "Early_Blight",
    "Late_Blight",
    "Leaf_Rust",
    "Mosaic_Virus",
    "Downy_Mildew",
    "Anthracnose",
    "Nutrient_Deficiency",
]

# Per-class centroid for [mean_R, mean_G, mean_B, texture_var, lesion_ratio, edge_density]
CENTROIDS = {
    "Healthy":              [60, 140, 60, 0.10, 0.02, 0.15],
    "Leaf_Blight":          [110, 100, 40, 0.35, 0.30, 0.40],
    "Powdery_Mildew":       [180, 180, 170, 0.25, 0.35, 0.30],
    "Bacterial_Spot":       [90, 110, 50, 0.40, 0.25, 0.45],
    "Early_Blight":         [120, 90, 40, 0.38, 0.28, 0.42],
    "Late_Blight":          [70, 80, 50, 0.45, 0.40, 0.50],
    "Leaf_Rust":            [150, 90, 40, 0.30, 0.33, 0.35],
    "Mosaic_Virus":         [100, 150, 70, 0.42, 0.20, 0.38],
    "Downy_Mildew":         [140, 160, 140, 0.28, 0.30, 0.28],
    "Anthracnose":          [80, 70, 40, 0.50, 0.45, 0.55],
    "Nutrient_Deficiency":  [170, 190, 90, 0.15, 0.10, 0.18],
}

SAMPLES_PER_CLASS = 220
# Feature-wise noise scale (RGB channels, texture_var, lesion_ratio, edge_density).
# Tuned so classes overlap somewhat, giving realistic ~85-90% held-out accuracy
# instead of a trivially separable synthetic dataset.
NOISE_SCALE = np.array([12, 12, 12, 0.07, 0.07, 0.07])


def generate_dataset():
    rows = []
    for label, centroid in CENTROIDS.items():
        centroid = np.array(centroid)
        samples = centroid + np.random.normal(0, 1.0, size=(SAMPLES_PER_CLASS, 6)) * NOISE_SCALE
        samples = np.clip(samples, 0, None)
        for s in samples:
            rows.append([*s, label])
    df = pd.DataFrame(rows, columns=[
        "mean_r", "mean_g", "mean_b", "texture_var", "lesion_ratio", "edge_density", "label"
    ])
    return df


def main():
    df = generate_dataset()
    X = df.drop(columns=["label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    clf = RandomForestClassifier(
        n_estimators=250, max_depth=12, random_state=RANDOM_STATE
    )
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Held-out accuracy: {acc * 100:.2f}% across {len(DISEASE_CLASSES)} classes")
    print(classification_report(y_test, preds))

    os.makedirs(os.path.join(os.path.dirname(__file__)), exist_ok=True)
    model_path = os.path.join(os.path.dirname(__file__), "crop_disease_model.pkl")
    joblib.dump({"model": clf, "classes": DISEASE_CLASSES}, model_path)
    print(f"Saved model to {model_path}")


if __name__ == "__main__":
    main()
