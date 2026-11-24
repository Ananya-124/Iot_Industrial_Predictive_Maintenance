"""Read newline-delimited JSON from a physical ESP32 USB serial port and POST it to the API."""
import argparse
import json
import time
import requests
import serial

parser = argparse.ArgumentParser()
parser.add_argument("--port", required=True, help="Example: COM5 on Windows or /dev/ttyUSB0 on Linux")
parser.add_argument("--baud", type=int, default=115200)
parser.add_argument("--api", default="http://127.0.0.1:8000/telemetry")
args = parser.parse_args()

with serial.Serial(args.port, args.baud, timeout=2) as device:
    print(f"Listening on {args.port} at {args.baud} baud")
    while True:
        line = device.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            response = requests.post(args.api, json=payload, timeout=3)
            response.raise_for_status()
            print(response.json())
        except (json.JSONDecodeError, requests.RequestException) as exc:
            print(f"Skipped line: {exc} | {line}")
