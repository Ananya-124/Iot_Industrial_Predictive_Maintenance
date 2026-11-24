from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Telemetry(BaseModel):
    device_id: str = Field(default="esp32-motor-01", min_length=1, max_length=64)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    vibration_x: float
    vibration_y: float
    vibration_z: float
    temperature_c: float
    current_a: float


class Prediction(BaseModel):
    condition: str
    confidence: float
    features: dict[str, float]
