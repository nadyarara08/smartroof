import streamlit as st
import pickle
import paho.mqtt.client as mqtt
import json
import numpy as np

# Load AI Model
with open("smartroof_model.pkl", "rb") as f:
    model = pickle.load(f)

status = "Menunggu data..."

def on_message(client, userdata, msg):
    global status
    data = json.loads(msg.payload.decode())

    X = np.array([[ 
        data["suhu"],
        data["hum"],
        data["ldr"],
        int(data["hujan"])
    ]])

    pred = model.predict(X)[0]

    label_map = {
        0: "☀️ CERAH",
        1: "⛅ MENDUNG",
        2: "⚠️ WASPADA HUJAN",
        3: "🌧️ HUJAN"
    }

    status = label_map[pred]

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883)
client.subscribe("AtapPintar/status")
client.on_message = on_message
client.loop_start()

# === UI ===
st.title("🏠 SmartRoof AI Monitoring")

st.metric("Status Cuaca AI", status)

st.caption("ESP32 • HiveMQ • Streamlit • AI")
