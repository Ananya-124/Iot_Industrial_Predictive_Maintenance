
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .schemas import Telemetry
from .features import extract_features
from .storage import initialize, insert_record, latest_records
from .model import load_model, FEATURE_NAMES
from .simulation import motor_simulation


app = FastAPI(
    title="Industrial Predictive Maintenance API",
    version="0.2.0",
)


class SimulationControl(BaseModel):
    scenario: Literal[
        "normal",
        "vibration",
        "overheating",
        "overcurrent",
        "combined",
    ] = "normal"

    severity: int = Field(default=70, ge=0, le=100)


@app.on_event("startup")
def startup():
    initialize()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": load_model() is not None,
    }


@app.post("/telemetry")
def receive_telemetry(item: Telemetry):
    features = extract_features(item)

    model = load_model()
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not trained. Run backend/scripts/train_model.py",
        )

    vector = [[features[name] for name in FEATURE_NAMES]]
    probabilities = model.predict_proba(vector)[0]

    best_index = int(probabilities.argmax())
    condition = str(model.classes_[best_index])
    confidence = float(probabilities[best_index])

    record = {
        "device_id": item.device_id,
        "timestamp": item.timestamp.isoformat(),
        **{
            k: float(v)
            for k, v in features.items()
            if k != "vibration_rms"
        },
        "vibration_rms": features["vibration_rms"],
        "condition": condition,
        "confidence": confidence,
        "raw_json": item.model_dump_json(),
    }

    insert_record(record)

    return {
        "accepted": True,
        "condition": condition,
        "confidence": confidence,
        "features": features,
    }


@app.get("/latest")
def latest(limit: int = 100):
    return latest_records(max(1, min(limit, 1000)))


@app.get("/summary")
def summary():
    records = latest_records(1000)

    if not records:
        return {
            "count": 0,
            "latest": None,
            "alerts": 0,
        }

    return {
        "count": len(records),
        "latest": records[-1],
        "alerts": sum(
            1 for record in records
            if record["condition"] != "normal"
        ),
    }


# ---------------- SIMULATION CONTROL ----------------

@app.get("/simulation/status")
def simulation_status():
    return motor_simulation.status()


@app.post("/simulation/start")
def start_simulation(control: SimulationControl):
    if load_model() is None:
        raise HTTPException(
            status_code=503,
            detail="AI model is not loaded. Train the model first.",
        )

    return motor_simulation.start(
        control.scenario,
        control.severity,
        lambda payload: receive_telemetry(Telemetry(**payload)),
    )


@app.put("/simulation/config")
def configure_simulation(control: SimulationControl):
    return motor_simulation.update(
        control.scenario,
        control.severity,
    )


@app.post("/simulation/stop")
def stop_simulation():
    return motor_simulation.stop()
