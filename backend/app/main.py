from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
import json
from .schemas import Telemetry
from .features import extract_features
from .storage import initialize, insert_record, latest_records
from .model import load_model, FEATURE_NAMES

app = FastAPI(title="Industrial Predictive Maintenance API", version="0.1.0")

@app.on_event("startup")
def startup():
    initialize()

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": load_model() is not None}

@app.post("/telemetry")
def receive_telemetry(item: Telemetry):
    features = extract_features(item)
    model = load_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not trained. Run backend/scripts/train_model.py")
    vector = [[features[name] for name in FEATURE_NAMES]]
    probabilities = model.predict_proba(vector)[0]
    best_index = int(probabilities.argmax())
    condition = str(model.classes_[best_index])
    confidence = float(probabilities[best_index])
    record = {
        "device_id": item.device_id,
        "timestamp": item.timestamp.isoformat(),
        **{k: float(v) for k, v in features.items() if k != "vibration_rms"},
        "vibration_rms": features["vibration_rms"],
        "condition": condition,
        "confidence": confidence,
        "raw_json": item.model_dump_json(),
    }
    insert_record(record)
    return {"accepted": True, "condition": condition, "confidence": confidence, "features": features}

@app.get("/latest")
def latest(limit: int = 100):
    return latest_records(max(1, min(limit, 1000)))

@app.get("/summary")
def summary():
    records = latest_records(1000)
    if not records:
        return {"count": 0, "latest": None, "alerts": 0}
    return {"count": len(records), "latest": records[-1],
            "alerts": sum(1 for r in records if r["condition"] != "normal")}
