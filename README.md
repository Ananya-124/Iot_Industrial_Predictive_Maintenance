# 5G + AI-Based Industrial Predictive Maintenance Using Edge Computing

Phase 1 starter: ESP32 firmware + Python API + SQLite + Random Forest + Streamlit.

## Architecture

`Motor/sensors -> ESP32 -> JSON telemetry -> FastAPI -> feature extraction + Random Forest -> SQLite -> Streamlit`

The same telemetry schema is used by the local simulator, serial receiver, and ESP32 firmware. This lets us replace simulated inputs with real sensors later without changing the API/dashboard.

## Project structure

- `firmware/esp32/`: Arduino firmware; emits one JSON object per line over Serial.
- `backend/app/`: FastAPI service, data validation, feature extraction, SQLite storage, ML inference.
- `backend/scripts/`: local telemetry simulator, serial receiver, synthetic training-data generator.
- `dashboard/`: Streamlit monitoring UI.
- `wokwi/`: starter Wokwi diagram and setup notes.
- `tests/`: basic API/model tests.

## Requirements

- Python 3.10+
- Arduino IDE 2.x or PlatformIO for firmware
- Wokwi (web editor or VS Code extension)

## Run the software locally (Windows PowerShell)

```powershell
cd industrial_predictive_maintenance
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend/scripts/train_model.py
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Open a second terminal, activate `.venv`, then:

```powershell
python backend/scripts/simulate_telemetry.py
```

Open a third terminal:

```powershell
streamlit run dashboard/app.py
```

- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://localhost:8501

The simulator posts generated readings to the local API. This validates backend, storage, ML inference and dashboard before hardware is available.

Run the basic checks from the project root with `python -m pytest -q`.

## Wokwi firmware test

Open `wokwi/diagram.json` in a Wokwi ESP32 DevKit v1 project and use `firmware/esp32/src/main.cpp` as the sketch (or copy it into `sketch.ino`). Start the simulation and inspect the Serial Monitor. Each output line should be valid JSON with `device_id`, `timestamp`, `vibration_x`, `vibration_y`, `vibration_z`, `temperature_c`, and `current_a`.

Wokwi's serial monitor is a visual test, not automatically the same as a local USB serial port. For a local serial-to-API test, use `serial_receiver.py` with a physical ESP32 COM port, or configure a Wokwi VS Code/CLI serial bridge in a later integration step.

## Important modeling note

The starter model is trained on clearly labelled **synthetic prototype data** so the pipeline can be tested. Its scores are not evidence of real machine-fault accuracy. We must collect and label actual normal/controlled-abnormal readings, then retrain and evaluate before making claims about predictive maintenance.

The initial output classes follow the project reference: `normal`, `abnormal_vibration`, `high_temperature`, `abnormal_current`. This is abnormal-condition classification, not remaining-useful-life/future-failure prediction.

## Safety

Do not connect a motor or 12V supply in Wokwi. Before physical assembly, verify motor startup/stall current, supply rating, ACS712 range, grounding and protection. Never connect a 5V analog output directly to an ESP32 ADC pin; confirm the divider and ADC range.
