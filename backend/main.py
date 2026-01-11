import json
import paho.mqtt.publish as publish
from config import MQTT_BROKER, TOPIC_CONTROL, TOPIC_MODE

def kirim_perintah(aksi, mode="AUTO", buzzer=0):
    payload = {
        "aksi": aksi,
        "mode": mode,
        "buzzer": buzzer
    }
    publish.single(
        TOPIC_CONTROL,
        json.dumps(payload),
        hostname=MQTT_BROKER
    )

def kirim_mode(mode):
    payload = {
        "mode": mode
    }
    publish.single(
        TOPIC_MODE,
        json.dumps(payload),
        hostname=MQTT_BROKER
    )
