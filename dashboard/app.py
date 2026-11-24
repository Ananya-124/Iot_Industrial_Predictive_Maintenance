
import time
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Industrial Predictive Maintenance",
    page_icon="🏭",
    layout="wide"
)

# ---------------- CONFIGURATION ----------------

API = st.sidebar.text_input(
    "Backend API",
    "http://127.0.0.1:8000"
)

auto = st.sidebar.toggle("Live auto refresh", value=True)
refresh = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 2)
limit = st.sidebar.slider("History records", 50, 1000, 300, 50)

# ---------------- HEADER ----------------

st.title("🏭 Industrial Predictive Maintenance")
st.caption(
    "5G + AI-based machine condition monitoring | "
    "ESP32 + Edge Computing + Random Forest"
)

# ---------------- FETCH DATA ----------------

try:
    health = requests.get(f"{API}/health", timeout=3)
    health.raise_for_status()

    response = requests.get(
        f"{API}/latest",
        params={"limit": limit},
        timeout=5
    )
    response.raise_for_status()

    records = response.json()

except requests.RequestException as exc:
    st.error(f"Backend connection failed: {exc}")
    st.info("Make sure FastAPI is running.")
    st.stop()

if not records:
    st.info("Waiting for ESP32 telemetry...")
    st.stop()

df = pd.DataFrame(records)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

if df.empty:
    st.warning("No valid telemetry timestamps found.")
    st.stop()

latest = df.iloc[-1]
status = str(latest["condition"]).lower()

# ---------------- MACHINE STATUS ----------------

st.subheader("Machine Overview")

if status == "normal":
    st.success("🟢 MACHINE STATUS: NORMAL")
else:
    st.error(f"🔴 MACHINE ALERT: {status.replace('_', ' ').upper()}")

# ---------------- KEY METRICS ----------------

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Temperature",
    f"{latest['temperature_c']:.2f} °C"
)

c2.metric(
    "Motor Current",
    f"{latest['current_a']:.3f} A"
)

c3.metric(
    "Vibration RMS",
    f"{latest['vibration_rms']:.3f}"
)

c4.metric(
    "AI Confidence",
    f"{latest['confidence']:.1%}"
)

c5.metric(
    "Total Readings",
    len(df)
)

# ---------------- ALERT SUMMARY ----------------

alerts = (df["condition"].str.lower() != "normal").sum()

a1, a2, a3 = st.columns(3)

a1.metric("Abnormal Readings", int(alerts))
a2.metric("Normal Readings", int(len(df) - alerts))
a3.metric(
    "Latest Device",
    str(latest["device_id"])
)

st.caption(
    f"Last telemetry received: "
    f"{latest['timestamp'].strftime('%d-%m-%Y %H:%M:%S')}"
)

# ---------------- SENSOR GRAPHS ----------------

st.divider()
st.subheader("📊 Live Sensor Monitoring")

left, right = st.columns(2)

with left:
    st.markdown("**Three-Axis Vibration**")

    fig = px.line(
        df,
        x="timestamp",
        y=["vibration_x", "vibration_y", "vibration_z"],
        labels={
            "value": "Acceleration (g, prototype units)",
            "timestamp": "Time",
            "variable": "Axis"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("**Motor Temperature**")

    fig = px.line(
        df,
        x="timestamp",
        y="temperature_c",
        labels={
            "temperature_c": "Temperature (°C)",
            "timestamp": "Time"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("**Motor Current**")

fig = px.line(
    df,
    x="timestamp",
    y="current_a",
    labels={
        "current_a": "Current (A)",
        "timestamp": "Time"
    }
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- ML PREDICTION HISTORY ----------------

st.divider()
st.subheader("🤖 AI Machine Condition History")

condition_counts = (
    df["condition"]
    .value_counts()
    .rename_axis("Condition")
    .reset_index(name="Readings")
)

fig = px.bar(
    condition_counts,
    x="Condition",
    y="Readings",
    title="Distribution of Predicted Machine Conditions"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- RECENT TELEMETRY ----------------

st.divider()
st.subheader("📡 Recent ESP32 Telemetry")

columns = [
    "timestamp",
    "device_id",
    "temperature_c",
    "current_a",
    "vibration_rms",
    "condition",
    "confidence"
]

st.dataframe(
    df[columns].tail(30).sort_values(
        "timestamp",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)

# ---------------- AUTO REFRESH ----------------

st.sidebar.caption(
    f"Last refresh: {time.strftime('%H:%M:%S')}"
)

if auto:
    time.sleep(refresh)
    st.rerun()
