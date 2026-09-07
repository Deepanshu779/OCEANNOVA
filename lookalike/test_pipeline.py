import json
import numpy as np
from shapely.geometry import Polygon

from lookalike.features.geometry import extract_geometric_features
from lookalike.features.radiometric import compute_radiometric_features
from lookalike.validation.baseline_rules import validate_spill
from lookalike.validation.ml_classifier import LookalikeMLClassifier
from lookalike.classification.output_schema import format_pipeline_output

def run_mock_test_suite():
    # Synthetic Input Samples (Simulating Task 2 AI Detections)
    test_samples = [
        {
            "spill_id": "SP-001",
            "ai_confidence": 0.92,
            "polygon": Polygon([[76.18, 10.82], [76.22, 10.83], [76.21, 10.80], [76.17, 10.81], [76.18, 10.82]]),
            "wind_speed_m_s": 6.5,
            # Distinct dark slick patch (sharp contrast)
            "patch_slick_val": 20,
            "patch_sea_val": 180
        },
        {
            "spill_id": "SP-002",
            "ai_confidence": 0.85,
            "polygon": Polygon([[76.50, 11.10], [76.51, 11.11], [76.51, 11.10], [76.50, 11.10]]),
            "wind_speed_m_s": 1.8, # Low wind threshold breach
            # Low contrast patch (calm sea / biogenic slick look-alike)
            "patch_slick_val": 100,
            "patch_sea_val": 110
        }
    ]

    # Initialize ML Classifier
    ml_clf = LookalikeMLClassifier()
    ml_clf.train_synthetic_baseline()

    results = []

    for sample in test_samples:
        # Mock 100x100 SAR Patch and Mask
        sar_patch = np.full((100, 100), sample["patch_sea_val"], dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 1
        sar_patch[30:70, 30:70] = sample["patch_slick_val"]

        # Feature Extraction
        geom_feats = extract_geometric_features(sample["polygon"])
        radio_feats = compute_radiometric_features(sar_patch, mask)

        # Validation Rule Engine
        rule_res = validate_spill(
            spill_id=sample["spill_id"],
            polygon=sample["polygon"],
            mean_contrast_ratio=radio_feats["mean_contrast_ratio"],
            wind_speed_m_s=sample["wind_speed_m_s"]
        )

        # ML Model Evaluation
        feature_vector = [
            geom_feats["area_km2"],
            geom_feats["compactness"],
            radio_feats["mean_contrast_ratio"],
            sample["wind_speed_m_s"],
            radio_feats["edge_gradient_sharpness"]
        ]
        ml_res = ml_clf.predict(feature_vector)

        # Final Schema Formatting
        is_valid = rule_res["valid_spill"] and ml_res["ml_valid_spill"]
        final_conf = min(rule_res["confidence"], ml_res["ml_confidence"])

        output_entry = format_pipeline_output(
            spill_id=sample["spill_id"],
            valid_spill=is_valid,
            confidence=final_conf,
            lookalike_prob=rule_res["lookalike_probability"],
            reasons=rule_res["reason"],
            geom_characterization=geom_feats
        )
        results.append(output_entry)

    print("--- MOCK TEST RESULTS ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_mock_test_suite()