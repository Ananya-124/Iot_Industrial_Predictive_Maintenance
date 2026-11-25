
import math
import random
import time
from datetime import datetime, timezone

import requests

API = "http://127.0.0.1:8000/telemetry"
DEVICE_ID = "motor-digital-twin-01"

SAMPLE_INTERVAL = 1.0
SCENARIO_DURATION = 30  # seconds per condition


def simulate_motor(t: float, scenario: str):
    """
    Generate synthetic motor sensor readings.

    t: elapsed simulation time in seconds
    scenario: normal, vibration, overheating, overcurrent, combined
    """

    # Normal motor baseline
    vibration_x = 0.18
    vibration_y = 0.16
    vibration_z = 0.20

    temperature = 30.0
    current = 0.45

    # Gradual fault development
    if scenario == "vibration":
        vibration_x += 0.9 * min(t / 15.0, 1.0)

    elif scenario == "overheating":
        temperature += 40.0 * min(t / 25.0, 1.0)

    elif scenario == "overcurrent":
        current += 1.7 * min(t / 10.0, 1.0)

    elif scenario == "combined":
        vibration_x += 0.9 * min(t / 15.0, 1.0)
        temperature += 40.0 * min(t / 25.0, 1.0)
        current += 1.7 * min(t / 10.0, 1.0)

    # Add small natural variations
    vibration_x += random.gauss(0, 0.04)
    vibration_y += random.gauss(0, 0.04)
    vibration_z += random.gauss(0, 0.04)

    temperature += random.gauss(0, 0.5)
    temperature += 0.2 * math.sin(t / 5.0)

    current += random.gauss(0, 0.05)

    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vibration_x": max(0.0, vibration_x),
        "vibration_y": max(0.0, vibration_y),
        "vibration_z": max(0.0, vibration_z),
        "temperature_c": temperature,
        "current_a": max(0.0, current),
    }


SCENARIOS = [
    "normal",
    "vibration",
    "overheating",
    "overcurrent",
    "combined",
]


if __name__ == "__main__":
    print("Motor Digital Twin started. Press Ctrl+C to stop.")

    start_time = time.time()

    while True:
        elapsed = time.time() - start_time

        scenario_index = int(elapsed // SCENARIO_DURATION) % len(SCENARIOS)
        scenario = SCENARIOS[scenario_index]

        scenario_time = elapsed % SCENARIO_DURATION
        payload = simulate_motor(scenario_time, scenario)

        try:
            response = requests.post(API, json=payload, timeout=3)
            response.raise_for_status()

            result = response.json()

            print(
                f"Scenario={scenario:12} "
                f"AI={result['condition']:22} "
                f"confidence={result['confidence']:.2f} "
                f"vibration={payload['vibration_x']:.2f} "
                f"temp={payload['temperature_c']:.1f}C "
                f"current={payload['current_a']:.2f}A"
            )

        except requests.RequestException as exc:
            print(f"Backend connection error: {exc}")

        time.sleep(SAMPLE_INTERVAL)
