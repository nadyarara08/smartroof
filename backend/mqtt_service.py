import threading
import paho.mqtt.client as mqtt
from config import MQTT_BROKER, TOPIC_SENSOR
from mqtt_logger import on_message

def _mqtt_loop():
    client = mqtt.Client(client_id="smartroof_backend")
    client.on_message = on_message

    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe(TOPIC_SENSOR)

    print("📡 MQTT service connected & subscribed")
    client.loop_forever()

def start_mqtt_thread():
    thread = threading.Thread(
        target=_mqtt_loop,
        daemon=True
    )
    thread.start()
