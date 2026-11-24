from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "random_forest.joblib"
FEATURE_NAMES = ["vibration_x", "vibration_y", "vibration_z", "vibration_rms", "temperature_c", "current_a"]


def train_prototype_model(seed: int = 42):
    rng = np.random.default_rng(seed)
    rows, labels = [], []
    # Synthetic, separable prototype patterns only; replace with measured labelled data.
    profiles = {
        "normal": (0.18, 0.18, 0.18, 30.0, 0.45),
        "abnormal_vibration": (1.15, 0.25, 0.25, 31.0, 0.50),
        "high_temperature": (0.20, 0.20, 0.20, 72.0, 0.48),
        "abnormal_current": (0.22, 0.22, 0.22, 32.0, 2.20),
    }
    for label, (vx, vy, vz, temp, current) in profiles.items():
        for _ in range(500):
            x, y, z = [max(0.0, rng.normal(v, 0.06 if v < 1 else 0.18)) for v in (vx, vy, vz)]
            rms = float(np.sqrt((x*x + y*y + z*z) / 3.0))
            rows.append([x, y, z, rms, rng.normal(temp, 2.0), max(0.0, rng.normal(current, 0.08 if current < 1 else 0.25))])
            labels.append(label)
    model = RandomForestClassifier(n_estimators=150, random_state=seed, class_weight="balanced")
    model.fit(np.asarray(rows), np.asarray(labels))
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)
