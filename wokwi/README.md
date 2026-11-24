# 5G + AI-Based Industrial Predictive Maintenance Using Edge Computing

An AI-powered industrial machine monitoring prototype that uses ESP32 telemetry, machine-learning-based condition classification, and a real-time dashboard to monitor motor operating conditions.

## Overview

Industrial motors are critical components in manufacturing environments. Unexpected machine abnormalities can cause production interruptions, equipment damage, and increased maintenance costs.

This project aims to develop an intelligent machine-monitoring system that collects sensor data, processes it using machine learning, and identifies abnormal operating conditions.

The prototype uses an ESP32 to collect vibration, temperature, and current measurements. A Python backend processes incoming telemetry using a Random Forest classifier, stores the results, and makes them available through a Streamlit dashboard.

The current software prototype uses simulated sensor readings through Wokwi. Physical sensor integration and 5G connectivity are planned extensions.

## Key Features

- **Real-time telemetry:** ESP32 sends machine sensor readings to a Python backend.
- **AI-based condition classification:** Random Forest classifies machine operating conditions.
- **Vibration monitoring:** Monitors three-axis vibration measurements.
- **Temperature monitoring:** Tracks motor temperature.
- **Current monitoring:** Tracks motor electrical current.
- **Edge-oriented architecture:** Designed to support local processing and reduced dependence on cloud infrastructure.
- **Interactive dashboard:** Streamlit displays sensor readings, machine status, predictions, and historical graphs.
- **Telemetry storage:** Stores sensor measurements and ML predictions for historical analysis.
- **Simulation support:** Wokwi and PlatformIO enable firmware testing before physical hardware assembly.

## System Architecture

```text
          ESP32 DevKit V1
                 |
       Sensor Data Collection
                 |
      +----------+----------+
      |          |          |
   ADXL345    DS18B20    ACS712
  Vibration  Temperature  Current
      |          |          |
      +----------+----------+
                 |
           Wi-Fi / 5G
                 |
          Python Backend
              FastAPI
                 |
        Feature Extraction
                 |
        Random Forest Model
                 |
       Machine Condition
          Classification
                 |
          SQLite Database
                 |
        Streamlit Dashboard
                 |
       Monitoring and Alerts
```

*The current Wokwi implementation simulates the sensor readings and communicates with the locally running FastAPI backend over the Wokwi Wi-Fi gateway. Physical sensors, Raspberry Pi edge deployment, and 5G networking are planned hardware/deployment stages.*

## Technologies Used

| Component               | Technology                       |
| ----------------------- | -------------------------------- |
| Microcontroller         | ESP32 DevKit V1                  |
| Firmware                | Embedded C++ / Arduino Framework |
| Firmware development    | PlatformIO                       |
| Simulation              | Wokwi                            |
| Backend                 | Python, FastAPI                  |
| Machine Learning        | Scikit-learn                     |
| ML Algorithm            | Random Forest Classifier         |
| Data Processing         | Pandas, NumPy                    |
| Database                | SQLite                           |
| Dashboard               | Streamlit                        |
| Visualization           | Plotly                           |
| Communication           | HTTP / JSON                      |
| Development Environment | Visual Studio Code               |

## Machine Operating Conditions

The current prototype simulates and classifies four operating conditions.

| Operating Condition | Description                                    |
| ------------------- | ---------------------------------------------- |
| Normal              | Motor operating within simulated normal ranges |
| Abnormal Vibration  | Increased vibration measurements               |
| High Temperature    | Elevated motor temperature                     |
| Abnormal Current    | Increased current consumption                  |

The ESP32 simulation automatically switches between these four conditions to test the complete telemetry and classification pipeline.

## Hardware Requirements

The planned physical prototype uses:

| Component                  | Purpose                                   |
| -------------------------- | ----------------------------------------- |
| ESP32 DevKit V1            | Sensor data acquisition and communication |
| ADXL345 Accelerometer      | Three-axis vibration measurement          |
| DS18B20 Temperature Sensor | Motor temperature measurement             |
| ACS712 5A Current Sensor   | Motor current measurement                 |
| 12V DC Geared Motor        | Industrial motor prototype                |
| Suitable 12V Power Supply  | Motor power supply                        |
| Motor Driver               | Motor control, where required             |

**Note:** The current implementation has been tested using simulated sensor data. Physical hardware integration is a subsequent development stage. Verify sensor voltage compatibility, motor startup/stall current, and electrical isolation before assembling the circuit.

## Software Requirements

Install the following before running the project:

- Python 3.10 or later
- Visual Studio Code
- PlatformIO IDE extension
- Wokwi extension for VS Code
- Git
- Internet connection for installing dependencies

## Project Structure

```text
Industrial-Predictive-Maintenance/
│
├── firmware/
│   └── esp32/
│       ├── src/
│       │   └── main.cpp
│       ├── platformio.ini
│       ├── wokwi.toml
│       └── diagram.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── features.py
│   │   ├── model.py
│   │   └── storage.py
│   │
│   ├── scripts/
│   │   ├── train_model.py
│   │   ├── simulate_telemetry.py
│   │   └── serial_receiver.py
│   │
│   └── models/
│
├── dashboard/
│   └── app.py
│
├── tests/
│
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Ananya-124/IoT_Industrial_Predictive_Maintenance.git
```

Navigate into the project:

```bash
cd YOUR_REPOSITORY
```

### 2. Create a Python Virtual Environment

```bash
python -m venv .venv
```

Activate it.

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Train the Machine Learning Model

Run the training script from the project root:

```bash
python backend/scripts/train_model.py
```

The trained Random Forest model is used by the backend to classify incoming machine telemetry.

**Important:** The current model is trained using synthetic data for prototype testing. Its predictions should not be interpreted as validated industrial failure predictions.

## Running the Project

The system uses three main components that should run simultaneously:

1. ESP32 firmware simulation.
2. FastAPI backend.
3. Streamlit dashboard.

### Step 1: Start the FastAPI Backend

From the project root, execute:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at:

- API: [http://localhost:8000](http://localhost:8000)
- API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- Latest telemetry: [http://localhost:8000/latest](http://localhost:8000/latest)
- Machine summary: [http://localhost:8000/summary](http://localhost:8000/summary)

### Step 2: Run ESP32 Firmware Using Wokwi

Open the ESP32 firmware project in Visual Studio Code.

Build the firmware:

```bash
cd firmware/esp32
pio run
```

Start the Wokwi simulator using the VS Code command palette:

```text
Ctrl + Shift + P
Wokwi: Start Simulator
```

The simulated ESP32 connects to:

```text
Wi-Fi SSID: Wokwi-GUEST
Password: (empty)
```

It sends sensor measurements to the FastAPI backend through:

```text
http://host.wokwi.internal:8000/telemetry
```

The Serial Monitor displays the transmitted JSON data and backend response.

### Step 3: Start the Streamlit Dashboard

Open another terminal from the project root:

```bash
streamlit run dashboard/app.py
```

Open the local dashboard:

[http://localhost:8501](http://localhost:8501)

The dashboard retrieves telemetry from FastAPI and displays machine operating conditions, sensor measurements, historical graphs, and model predictions.

## API Endpoints

| Method | Endpoint     | Description                                         |
| ------ | ------------ | --------------------------------------------------- |
| GET    | `/health`    | Checks backend and model availability               |
| POST   | `/telemetry` | Receives sensor data and generates an ML prediction |
| GET    | `/latest`    | Retrieves recent telemetry records                  |
| GET    | `/summary`   | Provides telemetry and abnormal-reading statistics  |

### Telemetry Request Example

The ESP32 sends measurements in JSON format:

```json
{
  "device_id": "esp32-wokwi-01",
  "vibration_x": 0.18,
  "vibration_y": 0.19,
  "vibration_z": 0.19,
  "temperature_c": 30.02,
  "current_a": 0.45
}
```

The backend automatically generates a timestamp when one is not supplied.

### Prediction Response Example

```json
{
  "accepted": true,
  "condition": "normal",
  "confidence": 0.99,
  "features": {
    "vibration_x": 0.18,
    "vibration_y": 0.19,
    "vibration_z": 0.19,
    "vibration_rms": 0.187,
    "temperature_c": 30.02,
    "current_a": 0.45
  }
}
```

## Machine Learning Workflow

The current machine-learning pipeline follows these stages:

1. Generate or collect machine sensor measurements.
2. Extract relevant features from the incoming telemetry.
3. Calculate vibration RMS from the three-axis vibration measurements.
4. Pass the extracted features to the trained Random Forest classifier.
5. Predict the operating condition.
6. Calculate prediction confidence.
7. Store sensor measurements and predictions.
8. Display results on the Streamlit dashboard.

The classifier currently identifies four simulated operating conditions:

- Normal
- Abnormal vibration
- High temperature
- Abnormal current

## Dashboard Features

The Streamlit dashboard provides:

- Current machine operating condition.
- Motor temperature readings.
- Motor current measurements.
- Three-axis vibration measurements.
- Vibration RMS.
- Random Forest prediction confidence.
- Normal and abnormal reading counts.
- Historical sensor graphs.
- Machine condition distribution.
- Recent telemetry records.
- Automatic dashboard refresh.

## Testing and Validation

The software prototype has been tested using Wokwi ESP32 simulation.

| Test                               | Result                       |
| ---------------------------------- | ---------------------------- |
| ESP32 firmware compilation         | Successful                   |
| Wokwi ESP32 simulation             | Successful                   |
| Wi-Fi connectivity                 | Successful                   |
| HTTP communication with FastAPI    | Successful                   |
| JSON telemetry validation          | Successful                   |
| Random Forest inference            | Successful                   |
| Telemetry storage                  | Verified through API         |
| Streamlit dashboard integration    | Implemented                  |
| Four-condition classification test | All four conditions detected |

The current validation uses simulated sensor readings and synthetic training data. Further testing with physical sensors and independently collected datasets is required.

## Current Limitations

- Sensor readings are currently simulated through Wokwi.
- The Random Forest model uses synthetic training data.
- The prototype demonstrates machine-condition classification rather than verified future failure prediction.
- Physical sensor calibration and validation are pending.
- Raspberry Pi 5 edge deployment is a planned extension.
- Actual 5G network communication and remote deployment are not yet implemented.

## Future Enhancements

- Integrate ADXL345, DS18B20, and ACS712 physical sensors.
- Deploy the backend and ML model on Raspberry Pi 5.
- Implement actual 5G connectivity for remote monitoring.
- Collect real-world motor operating data.
- Develop degradation-based predictive maintenance models.
- Introduce historical trend analysis and anomaly detection.
- Improve model evaluation using precision, recall, F1-score, and confusion matrices.
- Implement advanced maintenance alerts and notifications.
- Compare edge-processing and cloud-processing latency.

## Project Objective

The long-term objective is to develop an intelligent industrial monitoring system that combines IoT sensor acquisition, edge computing, machine learning, and high-speed connectivity to improve machine-condition monitoring and support predictive maintenance.

---

**Project Domain:** Internet of Things (IoT), Artificial Intelligence, Machine Learning, Edge Computing, Industrial Automation

**Status:** Software prototype implemented and tested using Wokwi simulation.

**Developed as an academic engineering project.**
