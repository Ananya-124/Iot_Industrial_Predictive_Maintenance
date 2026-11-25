
import time
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Industrial AI Control Room",
    page_icon="🏭",
    layout="wide",
)

# ---------------- STYLE ----------------

st.markdown("""
<style>
    .stApp {
        background: #0b1220;
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] {
        background: #111827;
    }
    [data-testid="stMetric"] {
        background: #111c2e;
        border: 1px solid #263449;
        padding: 16px;
        border-radius: 12px;
    }
    [data-testid="stMetricLabel"] {
        color: #9ca3af;
    }
    [data-testid="stMetricValue"] {
        color: #f8fafc;
    }
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    div[data-testid="stPlotlyChart"] {
        background: #111c2e;
        border: 1px solid #263449;
        border-radius: 12px;
        padding: 8px;
    }
    .status-panel {
        background: #111c2e;
        border: 1px solid #263449;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 12px;
    }
    .small-muted {
        color: #9ca3af;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- CONFIG ----------------

SCENARIOS = {
    "Normal Operation": "normal",
    "Vibration Fault": "vibration",
    "Overheating": "overheating",
    "Overcurrent": "overcurrent",
    "Combined Fault": "combined",
}

API = st.sidebar.text_input(
    "Backend API",
    "http://127.0.0.1:8000",
).rstrip("/")

auto_refresh = st.sidebar.toggle(
    "Live auto refresh",
    value=True,
)

refresh_seconds = st.sidebar.slider(
    "Refresh interval",
    1,
    10,
    2,
)

history_limit = st.sidebar.slider(
    "History records",
    50,
    1000,
    300,
    50,
)

st.sidebar.divider()
st.sidebar.caption("Industrial AI · Digital Twin Demo")
st.sidebar.caption("ESP32 / Edge AI / Random Forest")

# ---------------- HEADER ----------------

st.markdown(
    "<div class='small-muted'>INDUSTRIAL IoT · EDGE INTELLIGENCE</div>",
    unsafe_allow_html=True,
)

st.title("🏭 Industrial AI Control Room")
st.caption(
    "Motor condition monitoring and fault simulation"
)

# ---------------- FETCH SIMULATION STATUS ----------------

try:
    status_response = requests.get(
        f"{API}/simulation/status",
        timeout=3,
    )
    status_response.raise_for_status()
    sim_status = status_response.json()

except requests.RequestException as exc:
    st.error(f"Cannot reach simulation controller: {exc}")
    st.info("Make sure the FastAPI backend is running.")
    st.stop()

# ---------------- SIMULATION CONTROL ----------------

st.subheader("Simulation Control")

control_col1, control_col2, control_col3 = st.columns(
    [2, 1, 2]
)

with control_col1:
    selected_scenario_name = st.selectbox(
        "Fault scenario",
        list(SCENARIOS.keys()),
        index=list(SCENARIOS.values()).index(
            sim_status["scenario"]
        ),
    )

selected_scenario = SCENARIOS[selected_scenario_name]

with control_col2:
    severity = st.slider(
        "Fault severity",
        min_value=0,
        max_value=100,
        value=int(sim_status["severity"]),
        step=5,
        help="Controls the strength of the simulated fault.",
    )

with control_col3:
    st.markdown("**Simulation status**")

    if sim_status["running"]:
        st.success(
            f"RUNNING · {sim_status['scenario_name']}"
        )
    else:
        st.info("STOPPED · Ready to start")

    st.caption(
        f"Severity setting: {sim_status['severity']}%"
    )

button1, button2, button3 = st.columns(3)

with button1:
    if st.button(
        "▶ Start Simulation",
        use_container_width=True,
        type="primary",
    ):
        try:
            response = requests.post(
                f"{API}/simulation/start",
                json={
                    "scenario": selected_scenario,
                    "severity": severity,
                },
                timeout=5,
            )
            response.raise_for_status()
            st.success("Simulation started.")
            st.rerun()

        except requests.RequestException as exc:
            st.error(f"Could not start simulation: {exc}")

with button2:
    if st.button(
        "⚙ Apply Settings",
        use_container_width=True,
    ):
        try:
            response = requests.put(
                f"{API}/simulation/config",
                json={
                    "scenario": selected_scenario,
                    "severity": severity,
                },
                timeout=5,
            )
            response.raise_for_status()
            st.success("Scenario and severity updated.")
            st.rerun()

        except requests.RequestException as exc:
            st.error(f"Could not update settings: {exc}")

with button3:
    if st.button(
        "■ Stop Simulation",
        use_container_width=True,
    ):
        try:
            response = requests.post(
                f"{API}/simulation/stop",
                timeout=5,
            )
            response.raise_for_status()
            st.warning("Simulation stopped.")
            st.rerun()

        except requests.RequestException as exc:
            st.error(f"Could not stop simulation: {exc}")

st.divider()

# ---------------- FETCH TELEMETRY ----------------

try:
    health_response = requests.get(
        f"{API}/health",
        timeout=3,
    )
    health_response.raise_for_status()
    health = health_response.json()

    data_response = requests.get(
        f"{API}/latest",
        params={"limit": history_limit},
        timeout=5,
    )
    data_response.raise_for_status()
    records = data_response.json()

except requests.RequestException as exc:
    st.error(f"Backend data request failed: {exc}")
    st.stop()

# Keep this demo focused on the dashboard-controlled digital twin.
records = [
    record for record in records
    if record.get("device_id") == "motor-digital-twin-01"
]

# ---------------- MACHINE OVERVIEW ----------------

st.subheader("Machine Overview")

if not records:
    st.info(
        "No digital twin readings yet. Select a scenario "
        "and click Start Simulation."
    )
    df = pd.DataFrame()

else:
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )
    df = (
        df.dropna(subset=["timestamp"])
        .sort_values("timestamp")
    )

if not df.empty:
    latest = df.iloc[-1]
    condition = str(latest["condition"]).lower()
    confidence = float(latest["confidence"])

    if condition == "normal":
        st.success("🟢 MACHINE CONDITION: NORMAL")
    else:
        st.error(
            f"🔴 AI DETECTED: "
            f"{condition.replace('_', ' ').upper()}"
        )

    # ---------------- KPI CARDS ----------------

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric(
        "Temperature",
        f"{latest['temperature_c']:.1f} °C",
    )

    m2.metric(
        "Motor Current",
        f"{latest['current_a']:.2f} A",
    )

    m3.metric(
        "Vibration RMS",
        f"{latest['vibration_rms']:.3f}",
    )

    m4.metric(
        "AI Confidence",
        f"{confidence:.1%}",
    )

    m5.metric(
        "Readings",
        len(df),
    )

    st.caption(
        "Latest reading: "
        + latest["timestamp"].strftime("%d %b %Y · %H:%M:%S")
        + f" | Device: {latest['device_id']}"
    )

else:
    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric("Temperature", "—")
    m2.metric("Motor Current", "—")
    m3.metric("Vibration RMS", "—")
    m4.metric("AI Confidence", "—")
    m5.metric("Readings", "0")

# ---------------- SENSOR CHARTS ----------------

st.divider()
st.subheader("📈 Live Sensor Trends")

if not df.empty:
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("**Three-Axis Vibration**")

        vibration_fig = px.line(
            df,
            x="timestamp",
            y=[
                "vibration_x",
                "vibration_y",
                "vibration_z",
            ],
            labels={
                "value": "Vibration (prototype units)",
                "timestamp": "Time",
                "variable": "Axis",
            },
        )

        vibration_fig.update_layout(
            template="plotly_dark",
            height=330,
            margin=dict(l=10, r=10, t=25, b=10),
            legend_title_text="",
        )

        st.plotly_chart(
            vibration_fig,
            use_container_width=True,
        )

    with chart_right:
        st.markdown("**Temperature Trend**")

        temperature_fig = px.area(
            df,
            x="timestamp",
            y="temperature_c",
            labels={
                "temperature_c": "Temperature (°C)",
                "timestamp": "Time",
            },
        )

        temperature_fig.update_layout(
            template="plotly_dark",
            height=330,
            margin=dict(l=10, r=10, t=25, b=10),
        )

        st.plotly_chart(
            temperature_fig,
            use_container_width=True,
        )

    st.markdown("**Motor Current Trend**")

    current_fig = px.line(
        df,
        x="timestamp",
        y="current_a",
        labels={
            "current_a": "Current (A)",
            "timestamp": "Time",
        },
    )

    current_fig.update_layout(
        template="plotly_dark",
        height=280,
        margin=dict(l=10, r=10, t=25, b=10),
    )

    st.plotly_chart(
        current_fig,
        use_container_width=True,
    )

# ---------------- AI CONDITION DISTRIBUTION ----------------

st.divider()
st.subheader("🤖 AI Condition Analysis")

if not df.empty:
    analysis_left, analysis_right = st.columns(2)

    with analysis_left:
        counts = (
            df["condition"]
            .value_counts()
            .rename_axis("Condition")
            .reset_index(name="Readings")
        )

        condition_fig = px.pie(
            counts,
            names="Condition",
            values="Readings",
            hole=0.55,
        )

        condition_fig.update_layout(
            template="plotly_dark",
            height=320,
            margin=dict(l=10, r=10, t=25, b=10),
        )

        st.plotly_chart(
            condition_fig,
            use_container_width=True,
        )

    with analysis_right:
        alerts = int(
            (df["condition"].str.lower() != "normal").sum()
        )
        normal_count = int(len(df) - alerts)

        st.metric("Normal Predictions", normal_count)
        st.metric("Abnormal Predictions", alerts)

        st.caption(
            "Predictions are produced by the trained "
            "Random Forest model using synthetic telemetry."
        )

# ---------------- RECENT TELEMETRY ----------------

st.divider()
st.subheader("📡 Recent Digital Twin Telemetry")

if not df.empty:
    display_columns = [
        "timestamp",
        "device_id",
        "temperature_c",
        "current_a",
        "vibration_rms",
        "condition",
        "confidence",
    ]

    display_df = df[display_columns].tail(30).copy()
    display_df = display_df.sort_values(
        "timestamp",
        ascending=False,
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

# ---------------- FOOTER / REFRESH ----------------

st.divider()

st.caption(
    "Prototype demonstration · Synthetic motor telemetry · "
    f"AI model loaded: {'Yes' if health.get('model_loaded') else 'No'}"
)

st.sidebar.caption(
    f"Last refresh: {time.strftime('%H:%M:%S')}"
)

if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()
