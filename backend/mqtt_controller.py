import json
import time
import paho.mqtt.client as mqtt
from config import MQTT_BROKER, TOPIC_CONTROL

# =========================
# MQTT CLIENT SETUP
# =========================
client = mqtt.Client(client_id="SMARTROOF_BACKEND")

connected = False

def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        connected = True
        print("[MQTT] Connected to broker")
    else:
        print("[MQTT] Connection failed with code", rc)

client.on_connect = on_connect


def connect():
    global connected
    if not connected:
        try:
            client.connect(MQTT_BROKER, 1883)
            client.loop_start()
            time.sleep(1)
        except Exception as e:
            print("[MQTT] Reconnect failed:", e)



# =========================
# SEND COMMAND (SATU PINTU)
# =========================
def kirim_perintah(aksi, mode="AUTO", buzzer=0):
    """
    Kirim perintah ke ESP32
    
    aksi   : BUKA / TUTUP
    mode   : AUTO / MANUAL / FAILSAFE / TIMEOUT
    buzzer : jumlah bunyi (opsional)
    """

    connect()

    payload = {
        "aksi": aksi,
        "mode": mode
    }

    if buzzer > 0:
        payload["buzzer"] = buzzer

    client.publish(
        TOPIC_CONTROL,
        json.dumps(payload),
        qos=1
    )

    print(f"[MQTT] SEND → {payload}")
