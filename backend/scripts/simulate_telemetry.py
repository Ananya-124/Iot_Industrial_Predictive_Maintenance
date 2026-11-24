import math
import random
import time
from datetime import datetime, timezone
import requests

API = "http://127.0.0.1:8000/telemetry"


def sample(i: int):
    phase = (i // 20) % 4
    profiles = [
        (0.18, 0.18, 0.18, 30.0, 0.45),
        (1.15, 0.25, 0.25, 31.0, 0.50),
        (0.20, 0.20, 0.20, 72.0, 0.48),
        (0.22, 0.22, 0.22, 32.0, 2.20),
    ]
    vx, vy, vz, temp, current = profiles[phase]
    return {
        "device_id": "esp32-simulator-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vibration_x": max(0.0, random.gauss(vx, 0.05)),
        "vibration_y": max(0.0, random.gauss(vy, 0.05)),
        "vibration_z": max(0.0, random.gauss(vz, 0.05)),
        "temperature_c": random.gauss(temp, 1.0) + 0.2 * math.sin(i / 5),
        "current_a": max(0.0, random.gauss(current, 0.06)),
    }

if __name__ == "__main__":
    print("Posting simulated telemetry. Press Ctrl+C to stop.")
    i = 0
    while True:
        payload = sample(i)
        try:
            response = requests.post(API, json=payload, timeout=3)
            response.raise_for_status()
            result = response.json()
            print(f"{result['condition']:22} confidence={result['confidence']:.2f}  temp={payload['temperature_c']:.1f} C")
        except requests.RequestException as exc:
            print(f"API connection error: {exc}")
        i += 1
        time.sleep(1)
