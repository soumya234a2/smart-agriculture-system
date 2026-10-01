"""
Fertilizer recommendation engine.

Given the soil's Nitrogen (N), Phosphorus (P) and Potassium (K) levels
(in kg/ha), the current crop, and soil moisture, recommends a
fertilizer type and an approximate dosage. Thresholds are simplified,
commonly-cited agronomy guidelines meant to demonstrate the
recommendation pipeline end-to-end, not a substitute for a soil-testing
lab report.
"""

# Ideal NPK ranges per crop (kg/ha) — simplified reference values
CROP_NPK_TARGETS = {
    "rice":     {"N": 100, "P": 50, "K": 50},
    "wheat":    {"N": 120, "P": 60, "K": 40},
    "maize":    {"N": 150, "P": 75, "K": 60},
    "cotton":   {"N": 110, "P": 60, "K": 60},
    "sugarcane": {"N": 200, "P": 80, "K": 80},
    "default":  {"N": 120, "P": 60, "K": 50},
}

FERTILIZER_FOR_NUTRIENT = {
    "N": {"name": "Urea (46% N)", "unit_content": 0.46},
    "P": {"name": "DAP (18-46-0)", "unit_content": 0.46},
    "K": {"name": "MOP / Potash (60% K2O)", "unit_content": 0.60},
}


def recommend_fertilizer(n, p, k, crop="default"):
    """Returns a ranked list of fertilizer recommendations to close the
    gap between current soil NPK and the crop's target NPK."""
    target = CROP_NPK_TARGETS.get(crop.lower(), CROP_NPK_TARGETS["default"])
    deficits = {
        "N": max(target["N"] - n, 0),
        "P": max(target["P"] - p, 0),
        "K": max(target["K"] - k, 0),
    }

    recommendations = []
    for nutrient, deficit in sorted(deficits.items(), key=lambda x: x[1], reverse=True):
        if deficit <= 0:
            continue
        fert = FERTILIZER_FOR_NUTRIENT[nutrient]
        dosage_kg_per_ha = round(deficit / fert["unit_content"], 1)
        recommendations.append({
            "nutrient": nutrient,
            "deficit_kg_per_ha": round(deficit, 1),
            "fertilizer": fert["name"],
            "dosage_kg_per_ha": dosage_kg_per_ha,
        })

    if not recommendations:
        return {
            "crop": crop,
            "status": "balanced",
            "message": "Soil nutrient levels already meet the target range for this crop.",
            "recommendations": [],
        }

    return {
        "crop": crop,
        "status": "deficient",
        "message": f"{len(recommendations)} nutrient(s) below target for {crop}.",
        "recommendations": recommendations,
    }
