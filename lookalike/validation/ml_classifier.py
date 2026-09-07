import numpy as np
from sklearn.ensemble import RandomForestClassifier

class LookalikeMLClassifier:
    def __init__(self):
        # Features: [area_km2, compactness, contrast_ratio, wind_speed, gradient_sharpness]
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def train_synthetic_baseline(self):
        """Trains the classifier on synthetic sample vectors."""
        # Simulated Feature Matrix X: [area, compactness, contrast, wind, gradient]
        X = np.array([
            [12.5, 0.65, 2.3, 6.0, 18.5], # True Spill
            [18.0, 0.72, 2.1, 7.5, 21.0], # True Spill
            [0.4,  0.22, 1.1, 1.5, 4.2],  # Low Wind Look-alike
            [2.1,  0.15, 1.2, 5.0, 5.1],  # Biogenic Slick
            [15.2, 0.58, 2.8, 8.0, 19.2]  # True Spill
        ])
        y = np.array([1, 1, 0, 0, 1])  # 1 = Valid Spill, 0 = Look-alike
        
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, feature_vector: list) -> dict:
        """
        :param feature_vector: [area_km2, compactness, contrast_ratio, wind_speed, gradient_sharpness]
        """
        if not self.is_trained:
            self.train_synthetic_baseline()

        probs = self.model.predict_proba([feature_vector])[0]
        spill_prob, lookalike_prob = probs[1], probs[0]

        return {
            "ml_valid_spill": bool(spill_prob > 0.5),
            "ml_lookalike_prob": round(float(lookalike_prob), 2),
            "ml_confidence": round(float(spill_prob), 2)
        }