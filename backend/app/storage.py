import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parents[1] / "telemetry.db"


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            vibration_x REAL NOT NULL, vibration_y REAL NOT NULL, vibration_z REAL NOT NULL,
            temperature_c REAL NOT NULL, current_a REAL NOT NULL,
            vibration_rms REAL NOT NULL, condition TEXT NOT NULL,
            confidence REAL NOT NULL, raw_json TEXT NOT NULL
        )""")


def insert_record(record: dict[str, Any]):
    with connect() as conn:
        conn.execute("""INSERT INTO telemetry
            (device_id,timestamp,vibration_x,vibration_y,vibration_z,temperature_c,current_a,
             vibration_rms,condition,confidence,raw_json)
            VALUES (:device_id,:timestamp,:vibration_x,:vibration_y,:vibration_z,:temperature_c,
             :current_a,:vibration_rms,:condition,:confidence,:raw_json)""", record)


def latest_records(limit: int = 100):
    with connect() as conn:
        rows = conn.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in reversed(rows)]
