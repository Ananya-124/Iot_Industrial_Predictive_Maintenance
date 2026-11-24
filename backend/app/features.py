import math
from .schemas import Telemetry


def extract_features(item: Telemetry) -> dict[str, float]:
    # A single sample's vector magnitude is a simple prototype feature.
    # For real vibration analysis, compute RMS over a time window of many samples.
    vibration_rms = math.sqrt(
        (item.vibration_x ** 2 + item.vibration_y ** 2 + item.vibration_z ** 2) / 3.0
    )
    return {
        "vibration_x": item.vibration_x,
        "vibration_y": item.vibration_y,
        "vibration_z": item.vibration_z,
        "vibration_rms": vibration_rms,
        "temperature_c": item.temperature_c,
        "current_a": item.current_a,
    }
