import json
import paho.mqtt.client as mqtt
from config import *
from decision_engine import fail_safe_check
from mqtt_controller import kirim_perintah

MODE = "AUTO"

def on_message(client, userdata, msg):
    global MODE
    data = json.loads(msg.payload.decode())

    hujan = data.get("hujan", 0)

    command = fail_safe_check(hujan, MODE)

    if command:
        kirim_perintah(command)

client = mqtt.Client("SMARTROOF_FAILSAFE")
client.connect(MQTT_BROKER, 1883)
client.subscribe(TOPIC_SENSOR)
client.on_message = on_message

print("FAIL-SAFE LISTENER AKTIF")
client.loop_forever()
