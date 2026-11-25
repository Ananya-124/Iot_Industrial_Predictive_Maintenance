
import math
import random
import threading
import time
from datetime import datetime, timezone

SCENARIOS = {
    "normal": "Normal Operation",
    "vibration": "Vibration Fault",
    "overheating": "Overheating",
    "overcurrent": "Overcurrent",
    "combined": "Combined Fault",
}


class MotorSimulation:
    def __init__(self):
        self._lock = threading.Lock()
        self._thread = None
        self._stop_event = threading.Event()
        self._running = False
        self._scenario = "normal"
        self._severity = 70
        self._started_at = None

    def status(self):
        with self._lock:
            return {
                "running": self._running,
                "scenario": self._scenario,
                "scenario_name": SCENARIOS[self._scenario],
                "severity": self._severity,
                "started_at": self._started_at,
            }

    
    def start(self, scenario, severity, send_telemetry):
        with self._lock:
            if self._running:
                self._scenario = scenario
                self._severity = severity
            else:
                self._scenario = scenario
                self._severity = severity
                self._started_at = datetime.now(timezone.utc).isoformat()
                self._stop_event.clear()
                self._running = True

                self._thread = threading.Thread(
                    target=self._run,
                    args=(send_telemetry,),
                    daemon=True,
                )
                self._thread.start()

        return self.status()


   
    def update(self, scenario, severity):
        with self._lock:
            self._scenario = scenario
            self._severity = severity

        return self.status()


    def stop(self):
        self._stop_event.set()

        with self._lock:
            self._running = False

        return self.status()

    def _run(self, send_telemetry):
        elapsed = 0.0

        while not self._stop_event.is_set():
            with self._lock:
                scenario = self._scenario
                severity = self._severity

            payload = self._make_sample(elapsed, scenario, severity)

            try:
                send_telemetry(payload)
            except Exception as exc:
                print(f"Digital twin telemetry error: {exc}")

            elapsed += 1.0
            self._stop_event.wait(1.0)

        with self._lock:
            self._running = False

    def _make_sample(self, t, scenario, severity):
        # Severity is a percentage from 0 to 100.
        scale = severity / 100.0

        vibration_x = 0.18
        vibration_y = 0.16
        vibration_z = 0.20
        temperature = 30.0
        current = 0.45

        # Fault effects gradually develop over 15–25 seconds.
        progression = min(t / 20.0, 1.0)

        if scenario in ("vibration", "combined"):
            vibration_x += 0.9 * scale * progression

        if scenario in ("overheating", "combined"):
            temperature += 40.0 * scale * progression

        if scenario in ("overcurrent", "combined"):
            current += 1.7 * scale * progression

        vibration_x += random.gauss(0, 0.04)
        vibration_y += random.gauss(0, 0.04)
        vibration_z += random.gauss(0, 0.04)

        temperature += random.gauss(0, 0.5)
        temperature += 0.2 * math.sin(t / 5.0)

        current += random.gauss(0, 0.05)

        return {
            "device_id": "motor-digital-twin-01",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vibration_x": max(0.0, vibration_x),
            "vibration_y": max(0.0, vibration_y),
            "vibration_z": max(0.0, vibration_z),
            "temperature_c": temperature,
            "current_a": max(0.0, current),
        }


motor_simulation = MotorSimulation()
