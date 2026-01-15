import streamlit as st
import pandas as pd
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Smart Roof Admin",
    layout="wide"
)

st.title("📊 SMART ROOF ADMIN DASHBOARD")

# ===============================
# SENSOR DATA (REALTIME)
# ===============================
st.subheader("📡 Data Sensor Terakhir")

try:
    sensor = requests.get(f"{API_BASE}/api/sensor", timeout=3).json()

    if "error" in sensor:
        st.warning("Data sensor belum tersedia")
    else:
        st.json(sensor)

except Exception as e:
    st.error(f"Gagal mengambil data sensor: {e}")

# ===============================
# AI PREDICTION
# ===============================
st.subheader("🤖 Prediksi AI")

try:
    ai = requests.get(f"{API_BASE}/api/predict", timeout=5).json()
    st.json(ai)

except Exception as e:
    st.error(f"Gagal mengambil prediksi AI: {e}")

# ===============================
# HISTORICAL DATA
# ===============================
st.subheader("📈 Grafik Historis (24 Jam)")

try:
    history = requests.get(f"{API_BASE}/api/history/24h", timeout=5).json()

    if history["count"] == 0:
        st.warning("Belum ada data historis")
    else:
        df = pd.DataFrame(history["history"])
        df.set_index("time", inplace=True)

        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(df["suhu"])
        with col2:
            st.line_chart(df["kelembapan"])

        st.line_chart(df["cahaya"])

except Exception as e:
    st.error(f"Gagal load histori: {e}")

# ===============================
# SYSTEM STATUS
# ===============================
st.subheader("⚙️ Status Sistem")

try:
    health = requests.get(f"{API_BASE}/api/health").json()
    st.json(health)
except Exception as e:
    st.error(f"Gagal cek health: {e}")
