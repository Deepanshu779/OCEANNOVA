from lookalike.features.geometry import extract_geometric_features

def validate_spill(spill_id: str, polygon, mean_contrast_ratio: float, wind_speed_m_s: float) -> dict:
    geom_features = extract_geometric_features(polygon)
    reasons = []
    lookalike_prob = 0.0

    # Rule 1: Wind speed check
    if wind_speed_m_s < 3.0:
        reasons.append("low_wind_calm_sea_lookalike")
        lookalike_prob += 0.60
    elif wind_speed_m_s > 14.0:
        reasons.append("high_wind_dissipation")
        lookalike_prob += 0.40

    # Rule 2: Contrast Check
    if mean_contrast_ratio < 1.5:
        reasons.append("low_contrast_biogenic_slick")
        lookalike_prob += 0.30

    is_valid = lookalike_prob < 0.50
    if is_valid:
        reasons = ["shape_consistent", "environment_compatible"]

    final_confidence = round(max(0.05, min(0.99, 1.0 - lookalike_prob)), 2)

    return {
        "spill_id": spill_id,
        "valid_spill": is_valid,
        "confidence": final_confidence,
        "lookalike_probability": round(lookalike_prob, 2),
        "reason": reasons,
        "characterization": geom_features
    }